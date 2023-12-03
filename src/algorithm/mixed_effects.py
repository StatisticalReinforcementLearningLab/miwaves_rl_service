# src/algorithm/mixed_effects.py

# Imports
import copy
import numpy as np
import pandas as pd
import pickle as pkl
from src.algorithm.base import RLAlgorithm
from typing import Callable
import logging
import scipy.stats as stats
import scipy.linalg as linalg
import scipy.special as special
from functools import partial

import jax
import jax.numpy as jnp
import traceback

from sklearn.linear_model import LogisticRegression


@partial(jax.jit, static_argnums=(6, 7, 8, 9, 10))
def obj_func(
    flat_lower_t: jnp.array,
    noise_precision: float,
    A: jnp.array,
    B: jnp.array,
    mu_prior: jnp.array,
    sigma_prior: jnp.array,
    sum_sq_reward: int,
    size: int,
    nusers: int,
    ts: int,
    debug: bool = False,
):
    """Objective function for optimization"""

    # Construct the lower triangular matrix
    L = jnp.zeros((size, size), dtype=float)
    L = L.at[jnp.tril_indices(size)].set(flat_lower_t)

    # Construct the PSD matrix of random effects variance
    Sigma_u = L @ L.T
    del L

    # Construct X and y
    # X = jnp.linalg.inv(jnp.array(sigma_prior) + jnp.kron(jnp.identity(nusers), Sigma_u))
    X = MixedEffectsAlgorithm.invert_sigma_theta(sigma_prior, Sigma_u, nusers)

    y = noise_precision

    # Evaluate the optimization function
    s1, part1 = jnp.linalg.slogdet(X)
    s2, part2 = jnp.linalg.slogdet(X + y * A)
    part2 = (-1) * part2
    # part3 = nusers * ts * jnp.log(y)
    part3 = ts * jnp.log(y)
    part4 = -1 * y * sum_sq_reward
    part5 = -1 * mu_prior.T @ X @ mu_prior
    part6 = (
        (X @ mu_prior + y * B).T @ jnp.linalg.inv(X + y * A) @ (X @ mu_prior + y * B)
    )

    if debug:
        print("Part 1: ", -part1)
        print("Part 2: ", -part2)
        print("Part 3: ", -part3)
        print("Part 4: ", -part4)
        print("Part 5: ", -part5)
        print("Part 6: ", -part6)

    # Check mixed effects model overleaf file, section 5.4, page 20, equation 171
    # Doing negative because we are minimizing
    result = -1 * (part1 + part2 + part3 + part4 + part5 + part6)

    del part1
    del part2
    del part3
    del part4
    del part5
    del part6

    return result


class MixedEffectsAlgorithm(RLAlgorithm):
    """Mixed Effects Model based RL algorithm"""

    def __init__(
        self,
        num_days: int,
        prior_mean: np.array,
        prior_cov: np.array,
        init_cov_u: np.array,
        init_noise_var: float,
        alloc_func: Callable,
        max_iter: int = 500,
        learning_rate: float = 0.001,
        tolerance: float = 1e-6,
        starting_time_of_day: int = 0,
        rng: np.random.RandomState = None,
        maxseed: int = 2**16 - 1,
        debug: bool = False,
        logger_path: str = None,
        param_size: list = [8, 8, 8],
    ) -> None:
        """
        Initialize the mixed effects model based RL algorithm
        :param num_days: number of days
        :param prior_mean: prior mean
        :param prior_cov: prior covariance
        :param init_cov_u: initial random effects covariance matrix
        :param init_noise_var: initial noise variance
        :param alloc_func: allocation function
        :param max_iter: maximum number of iterations
        :param learning_rate: learning rate
        :param tolerance: tolerance for convergence
        :param starting_time_of_day: starting time of day
        :param rng: random number generator
        :param maxseed: maximum seed value
        :param debug: debug flag
        :param logger_path: path to log file
        """

        # TODO: Decide how the starting time of day works

        self.num_days = num_days
        self.prior_mean = prior_mean
        self.prior_cov = prior_cov
        self.sigma_u = init_cov_u
        self.init_noise_var = init_noise_var
        self.noise_var = init_noise_var

        self.theta_pop_mean = copy.deepcopy(self.prior_mean)
        self.theta_pop_cov = copy.deepcopy(self.prior_cov)

        cholesky = np.linalg.cholesky(self.sigma_u)
        self.ltu_flat = cholesky[np.tril_indices(self.sigma_u.shape[0])].flatten()
        self.init_ltu_flat = copy.deepcopy(self.ltu_flat)

        self.allocation_function = alloc_func
        self.current_study_decision_point = 0
        self.time_of_day = starting_time_of_day

        self.max_iter = max_iter
        self.learning_rate = learning_rate
        self.tolerance = tolerance
        self.rng = rng
        self.maxseed = maxseed
        self.bernoulli = stats.bernoulli
        self.user_data = {}
        self.num_users = 0

        self.policyid = 0
        self.param_size = param_size

        self.hyperparam_update_flag = False

        self.posterior_mean = None
        self.posterior_cov = None
        self.posterior_mean_history = []
        self.posterior_cov_history = []
        self.sigma_u_history = []
        self.noise_var_history = []
        self.theta_pop_posterior_mean_history = []
        self.theta_pop_posterior_cov_history = []
        self.debug = debug

        self.last_update_users_list = []
        self.last_hyperparam_update_id = 0

        self.user_list = []

        # Logging stuff
        logfile = logger_path + "/RL_log.txt"
        self.logger = logging.getLogger("MixedEffects")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(logfile, mode="w")
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)

    def clip_prob(self, prob, min: float = 0.2, max: float = 0.8):
        """Clip the probability to be between min and max"""
        return np.clip(prob, min, max)

    @staticmethod
    def validate_matrix(
        flat_lower_t: jnp.array,
        noise_precision: float,
        A: jnp.array,
        B: jnp.array,
        mu_prior: jnp.array,
        sigma_prior: jnp.array,
        sum_sq_reward: int,
        size: int,
        nusers: int,
        ts: int,
        debug: bool = False,
    ):
        """
        Objective function for optimization, but also checks
        if the resulting posterior is going to be PSD and within
        reasonable limits
        """
        # Construct the lower triangular matrix
        L = jnp.zeros((size, size), dtype=float)
        L = L.at[jnp.tril_indices(size)].set(flat_lower_t)

        # Construct the PSD matrix of random effects variance
        Sigma_u = L @ L.T
        del L

        # Construct X and y
        # X = jnp.linalg.inv(jnp.array(sigma_prior) + jnp.kron(jnp.identity(nusers), Sigma_u))
        X = MixedEffectsAlgorithm.invert_sigma_theta(sigma_prior, Sigma_u, nusers)
        y = noise_precision

        eigvals = jnp.min(jnp.linalg.eigh(X + y * A)[0])

        if eigvals <= 0 or jnp.isnan(eigvals):
            return 100000, False

        newpost_var = jnp.linalg.inv(X + y * A)

        eigvals = jnp.min(jnp.linalg.eigh(newpost_var)[0])

        if eigvals <= 0 or jnp.isnan(eigvals):
            return 100000, False

        temp_mean = X @ mu_prior + y * B
        newpost_mean = newpost_var @ temp_mean

        # Do the sanity checks

        # If any diagonal entry in the covariance matrix is less than 0
        if jnp.min(jnp.diag(newpost_var)) < 0:
            return 100000, False

        # If absolute value of any posterior mean entry is greater than 10 (need to think
        # about this sanity check)
        if jnp.max(jnp.abs(newpost_mean).flatten()) > 10:
            return 100000, False

        # Evaluate the optimization function
        s1, part1 = jnp.linalg.slogdet(X)
        s2, part2 = jnp.linalg.slogdet(X + y * A)
        part2 = (-1) * part2
        part3 = ts * jnp.log(y)
        part4 = -1 * y * sum_sq_reward
        part5 = -1 * mu_prior.T @ X @ mu_prior
        part6 = temp_mean.T @ newpost_mean

        # Check mixed effects model overleaf file, section 5.4, page 20, equation 171
        # Doing negative because we are minimizing
        result = -1 * (part1 + part2 + part3 + part4 + part5 + part6)
        del part1
        del part2
        del part3
        del part4
        del part5
        del part6
        return result, True

    @staticmethod
    def invert_sigma_theta(Sigma_0: jnp.array, Sigma_u: jnp.array, nusers: int):
        """
        Invert the covariance matrix efficiently
        """
        C = jnp.linalg.inv(Sigma_u)
        D = -jnp.linalg.inv(Sigma_u + nusers * Sigma_0) @ Sigma_0 @ C

        inverse = jnp.kron(jnp.ones((nusers, nusers)), D) + jnp.kron(
            jnp.identity(nusers), C
        )

        return inverse

    def create_A_B_matrix(self):
        """
        Create the design matrix and reward matrix up until the current
        decision point using design rows and reward history for each user
        """
        design_matrix = []
        reward_matrix = []
        indexes = [0]
        update_user_list = []
        total_timesteps = 0
        total_update_users = 0

        for i in self.user_list:
            if (
                self.user_data[i]["design_state"][1:-1] == []
                or self.user_data[i]["reward"][1:] == []
            ):
                continue
            design_matrix.append(self.user_data[i]["design_state"][1:-1])
            reward_matrix.append(self.user_data[i]["reward"][1:])
            indexes.append(indexes[-1] + len(self.user_data[i]["design_state"][1:-1]))
            update_user_list.append(i)
            total_timesteps += len(self.user_data[i]["design_state"][1:-1])
            total_update_users += 1

        design_matrix = np.vstack(design_matrix)
        reward_matrix = np.hstack(reward_matrix)

        A_hat = [
            design_matrix[indexes[i] : indexes[i + 1]].T
            @ design_matrix[indexes[i] : indexes[i + 1]]
            for i in range(total_update_users)
        ]

        A = linalg.block_diag(*A_hat)

        B = np.array(
            [
                design_matrix[indexes[i] : indexes[i + 1]].T
                @ reward_matrix[indexes[i] : indexes[i + 1]]
                for i in range(total_update_users)
            ]
        ).flatten()

        sum_sq_reward = 0
        for i in range(len(reward_matrix)):
            sum_sq_reward += reward_matrix[i] ** 2

        return A, B, A_hat, sum_sq_reward, total_timesteps, update_user_list

    def get_action(
        self, user_id: str, state: np.ndarray, decision_time: int, seed: int = -1
    ) -> tuple[int, int, float, int, int]:
        """
        Get action
        :param user_id: user id of the user
        :param state: state of the user
        :param decision_time: decision time of the user for which action is to be taken
        :param seed: seed for random number generator
        :return: action, seed, probability of taking action, and policy id
        """

        if len(state) != 3:
            raise ValueError("State should be of length 3")

        # Compute the advantage
        advantage_default = [
            1,
            state[0],
            state[1],
            state[2],
            state[0] * state[1],
            state[0] * state[2],
            state[1] * state[2],
            state[0] * state[1] * state[2],
        ]

        advantage_with_intercept = np.array(advantage_default[: self.param_size[2]])

        num_params = np.sum(self.param_size)

        # If the user is new, add the user to the user list
        # if user_id not in self.user_list:
        #     self.user_list.append(user_id)
        #     self.num_users += 1

        #     user = self.user_list.index(user_id)

        #     # Initialize the user data matrix
        #     self.user_data[user] = {
        #         "state": [[]],
        #         "action": [None],
        #         "act_prob": [None],
        #         "reward": [],
        #         "design_state": [None],
        #     }
        if user_id not in self.last_update_users_list:
            # Since user is new, sample for the current posterior of theta pop
            posterior_mean_user = self.theta_pop_mean
            posterior_cov_user = self.theta_pop_cov + self.sigma_u

        else:
            # Otherwise get the user index and corresponding posteriors
            user = self.user_list.index(user_id)
            posterior_mean_user = self.posterior_mean[
                user * num_params : (user + 1) * num_params
            ]
            posterior_cov_user = self.posterior_cov[
                user * num_params : (user + 1) * num_params,
                user * num_params : (user + 1) * num_params,
            ]

        # Compute the posterior mean of the adv term
        beta_mean = np.array(posterior_mean_user[-self.param_size[2] :])

        # Compute the posterior covariance of the adv term
        beta_cov = np.array(
            posterior_cov_user[-self.param_size[2] :, -self.param_size[2] :]
        )

        # Compute the posterior mean of the adv*beta distribution
        adv_beta_mean = advantage_with_intercept.T.dot(beta_mean)

        # Compute the posterior variance of the adv*beta distribution
        adv_beta_var = advantage_with_intercept.T @ beta_cov @ advantage_with_intercept

        # Call the allocation function
        prob = self.allocation_function(mean=adv_beta_mean, var=adv_beta_var)

        # If the probability is NaN, set it to 0.5, and log the error
        if np.isnan(prob):
            self.logger.error(
                f"[{self.current_study_decision_point}] Probability NaN encountered for user: {user}"
            )
            self.logger.error(f"BETA_MEAN: {beta_mean} VAR: {beta_cov}")
            self.logger.error(f"ADV_BETA: {adv_beta_mean} VAR: {adv_beta_var}")
            self.logger.error(f"POST_MEAN: {posterior_mean_user}")
            self.logger.error(f"POST_VAR: {posterior_cov_user}")
            prob = 0.5
            # TODO: Decide whether this is a good idea to handle the exception with 0.5 probability here

        # Clip the probability
        act_prob = self.clip_prob(prob)

        # Create the rng object using the class rng
        if seed != -1:
            rng = np.random.default_rng(seed=seed)
        else:
            seed = self.rng.integers(low=0, high=self.maxseed)
            rng = np.random.default_rng(seed=seed)

        # Sample the action from the bernoulli distribution
        action = rng.binomial(1, act_prob)

        # Log event to logger
        if self.debug:
            self.logger.info(
                f"[{self.current_study_decision_point}] \
                    User: {user_id} State: {state} \
                        Decision Time: {decision_time} \
                            Seed: {seed} \
                                Prob: {prob} \
                                    Act Prob: {act_prob} \
                                        Action: {action}"
            )
            print(
                user_id,
                state,
                decision_time,
                seed,
                prob,
                act_prob,
                action,
                self.current_study_decision_point,
            )

        # Not saving now, as we are saving all this in db.
        # will update when the decision window ends

        # Update the user data
        # self.user_data[user]["action"].append(action)
        # self.user_data[user]["act_prob"].append(act_prob)

        # # Update the design state
        # self.user_data[user]["design_state"].append(self.update_design_row(user))

        return action, int(seed), act_prob, self.policyid

    def update_hyperparameters(
        self, request_id: int, data: pd.DataFrame, use_data: bool = False, debug: bool = False
    ) -> None:
        """
        Update the hyperparameters
        :param request_id: request id
        :param data: data to update algorithm
        :param use_data: whether to use data or not, or use the user_data
        :param debug: debug flag
        :return: None
        """

        # TODO: Update just using the data in the dataframe

        # Check for dataframe columns
        if use_data:
            raise NotImplementedError("use_data is not implemented yet")

        # Create the A, B matrix
        (
            A,
            B,
            A_hat,
            sum_sq_reward,
            total_ts,
            update_user_list,
        ) = self.create_A_B_matrix()

        if debug:
            # Log event to logger
            self.logger.debug(
                "Updating hyperparameters for users: {}".format(update_user_list)
            )

        total_update_users = len(update_user_list)
        init_ltu_flat = copy.deepcopy(self.ltu_flat)
        init_noise_var_inv = 1.0 / self.noise_var
        min_ltu_flat = copy.deepcopy(self.ltu_flat)
        min_noise_var_inv = init_noise_var_inv
        skip_count = 0
        last_update_index = -1
        reset_flag = False
        sigma_u_shape = self.sigma_u.shape[0]

        lr = lr2 = self.learning_rate

        mu_0 = np.kron(np.ones(total_update_users), self.prior_mean)

        old_obj, valid = MixedEffectsAlgorithm.validate_matrix(
            init_ltu_flat,
            init_noise_var_inv,
            A,
            B,
            mu_0,
            self.prior_cov,
            sum_sq_reward,
            sigma_u_shape,
            total_update_users,
            total_ts,
        )

        # Log event to logger
        if debug:
            self.logger.debug("Initial Objective: {}, Valid: {}".format(old_obj, valid))

        if not valid:
            init_ltu_flat = copy.deepcopy(self.init_ltu_flat)
            init_noise_var_inv = copy.deepcopy(self.init_noise_var)
            min_noise_var_inv = init_noise_var_inv
            old_obj, valid = MixedEffectsAlgorithm.validate_matrix(
                init_ltu_flat,
                init_noise_var_inv,
                A,
                B,
                mu_0,
                self.prior_cov,
                sum_sq_reward,
                sigma_u_shape,
                total_update_users,
                total_ts,
            )

            # Log event to logger
            if debug:
                self.logger.debug(
                    "Initial Objective after reset: {}, Valid: {}".format(
                        old_obj, valid
                    )
                )

            if not valid:
                if debug:
                    self.logger.error("Initial Objective is not valid after reset")
                return

        min_obj = copy.deepcopy(old_obj)
        # Log event to logger
        if debug:
            self.logger.debug("Starting optimization with objective: {}", old_obj)

        # Do the optimization
        for idx in range(self.max_iter):
            # Compute the gradient
            jacob = jax.grad(obj_func, argnums=0)(
                init_ltu_flat,
                init_noise_var_inv,
                A,
                B,
                mu_0,
                self.prior_cov,
                sum_sq_reward,
                sigma_u_shape,
                total_update_users,
                total_ts,
            )
            grad = jax.grad(obj_func, argnums=1)(
                init_ltu_flat,
                init_noise_var_inv,
                A,
                B,
                mu_0,
                self.prior_cov,
                sum_sq_reward,
                sigma_u_shape,
                total_update_users,
                total_ts,
            )

            new_ltu_flat = init_ltu_flat - lr * jacob

            # Update the value of the noise variance
            if init_noise_var_inv - lr2 * grad > 0.0001:
                new_noise_var_inv = init_noise_var_inv - (lr2 * grad)

            else:
                new_noise_var_inv = init_noise_var_inv
                lr2 = lr2 / 2

            obj_val, valid = MixedEffectsAlgorithm.validate_matrix(
                new_ltu_flat,
                new_noise_var_inv,
                A,
                B,
                mu_0,
                self.prior_cov,
                sum_sq_reward,
                sigma_u_shape,
                total_update_users,
                total_ts,
            )

            # Reduce the learning rate if objective is either null (i.e. invalid Sigma_u
            # or objective value explodes, or objective value goes negative, or the resulting
            # posteriors will be invalid i.e. either mean is too big, or variance is negative
            # for the diagonal entries)
            if jnp.isnan(obj_val) or obj_val > 10 * min_obj or obj_val < 0 or not valid:
                lr = lr / 2
                skip_count += 1
            else:
                if obj_val < min_obj:
                    min_ltu_flat = new_ltu_flat
                    init_noise_var_inv = new_noise_var_inv
                    min_obj = obj_val
                    last_update_index = idx
                init_ltu_flat = new_ltu_flat
                init_noise_var_inv = new_noise_var_inv
                skip_count = 0

            if debug:
                self.logger.debug(
                    "Iteration: {}, Noise variance: {}, Objective: {}, Valid: {}, Nan: {}".format(
                        idx, init_noise_var_inv, obj_val, valid, jnp.isnan(obj_val)
                    )
                )

            # Check if the change in objective value is small
            if np.abs(obj_val - old_obj) < self.tolerance or (idx == self.max_iter - 1):
                if debug:
                    self.logger.debug(
                        "Converged at iteration: {} with value {}".format(
                            idx, 1.0 / min_noise_var_inv
                        )
                    )
                    self.logger.debug("Sigma_U: {}".format(min_ltu_flat))
                break

            # Restart if we haven't gone below the previous objective value
            if (idx - last_update_index) > 250 or skip_count > 10:
                if reset_flag:
                    # Reset already done once, so just terminate
                    if debug:
                        self.logger.debug(
                            "Converged at iteration: {} with value {}".format(
                                idx, 1.0 / min_noise_var_inv
                            )
                        )
                        self.logger.debug("Sigma_U: {}".format(min_ltu_flat))
                    break
                else:
                    # Reset back to initial params
                    init_ltu_flat = self.init_ltu_flat
                    init_noise_var_inv = self.init_noise_var
                    lr = lr2 = self.learning_rate
                    last_update_index = idx
                    skip_count = 0
                    reset_flag = True

                    if debug:
                        self.logger.debug("Resetting at iteration: {}".format(idx))

            elif skip_count == 0:
                old_obj = obj_val

        # Set the new noise variance and assign it a pending status
        self.noise_var_pending = 1.0 / min_noise_var_inv

        # Update the sigma_u
        self.ltu_flat_pending = min_ltu_flat

        L = np.zeros(self.sigma_u.shape, dtype=float)
        L[np.tril_indices(sigma_u_shape)] = self.ltu_flat_pending
        self.sigma_u_pending = L @ L.T
        self.hyperparam_requestid_pending = request_id

        # Set the flag to update the hyperparameters
        self.hyperparam_update_flag = True

    def update_posteriors(
        self, data: pd.DataFrame, use_data: bool = False, debug: bool = False
    ) -> None:
        """
        Update the posteriors using the data upto the current decision point
        """

        if self.debug:
            # Log event to logger
            self.logger.debug("Updating posteriors for users")

        # TODO: Update just using the data in the dataframe
        if use_data:
            raise NotImplementedError("use_data is not implemented yet")

        # Check if the hyperparameters have been updated
        if self.hyperparam_update_flag:
            self.sigma_u = copy.deepcopy(self.sigma_u_pending)
            self.noise_var = copy.deepcopy(self.noise_var_pending)
            self.ltu_flat = copy.deepcopy(self.ltu_flat_pending)

            # Save in history
            self.sigma_u_history.append(np.array(self.sigma_u))
            self.noise_var_history.append(self.noise_var)

            # Reset the flag
            self.hyperparam_update_flag = False
            self.last_hyperparam_update_id = self.hyperparam_requestid_pending

            # Log event to logger
            self.logger.debug(
                "Hyperparameters updated for request id {} and used for posterior update".format(
                    self.last_hyperparam_update_id
                )
            )

        (
            A,
            B,
            A_hat,
            _,
            _,
            update_user_list,
        ) = self.create_A_B_matrix()

        total_update_users = len(update_user_list)
        mu_0 = np.kron(np.ones(total_update_users), self.prior_mean)

        Sigma_theta_t = np.kron(
            np.ones((total_update_users, total_update_users)), self.prior_cov
        ) + np.kron(np.identity(total_update_users), self.sigma_u)

        sigma_theta_t_inverse = np.linalg.inv(Sigma_theta_t)

        # Compute the posterior covariance
        self.posterior_cov = np.linalg.inv(
            sigma_theta_t_inverse + (1.0 / self.noise_var) * A
        )

        # Compute the posterior covariance
        self.posterior_mean = self.posterior_cov @ (
            sigma_theta_t_inverse @ mu_0.reshape(-1, 1)
            + (1.0 / self.noise_var * B).reshape(-1, 1)
        )

        # Compute the theta pop posterior mean

        zeta1 = zeta2 = zeta3 = zeta4 = None
        m_inv = 1.0 / total_update_users

        B_hat = np.array(B).reshape(total_update_users, -1)

        for i in range(total_update_users):
            psi = self.noise_var * np.linalg.inv(self.sigma_u) + A_hat[i]
            psi_inv = np.linalg.inv(psi)
            z1 = B_hat[i]
            z2 = np.array(A_hat[i]) @ psi_inv @ B_hat[i]
            z3 = np.array(A_hat[i])
            z4 = np.array(A_hat[i]) @ psi_inv @ np.array(A_hat[i])
            zeta1 = z1 if zeta1 is None else zeta1 + z1
            zeta2 = z2 if zeta2 is None else zeta2 + z2
            zeta3 = z3 if zeta3 is None else zeta3 + z3
            zeta4 = z4 if zeta4 is None else zeta4 + z4

        zeta1 = m_inv * np.array(zeta1)
        zeta2 = m_inv * np.array(zeta2)
        zeta3 = m_inv * np.array(zeta3)
        zeta4 = m_inv * np.array(zeta4)

        E = (
            m_inv * np.linalg.inv(self.prior_cov)
            + (1.0 / self.noise_var) * zeta3
            - (1.0 / self.noise_var) * zeta4
        )

        E_inv = np.linalg.inv(E)

        self.theta_pop_mean = E_inv @ (
            m_inv * np.linalg.inv(self.prior_cov) @ self.prior_mean.reshape(-1, 1)
            + (1.0 / self.noise_var) * zeta1.reshape(-1, 1)
            - (1.0 / self.noise_var) * zeta2.reshape(-1, 1)
        )

        # Compute the theta pop posterior covariance
        self.theta_pop_cov = m_inv * E_inv

        # Update the posterior mean and covariance history
        self.posterior_mean_history.append(self.posterior_mean)
        self.posterior_cov_history.append(self.posterior_cov)
        self.theta_pop_posterior_mean_history.append(self.theta_pop_mean)
        self.theta_pop_posterior_cov_history.append(self.theta_pop_cov)

        self.last_update_users_list = update_user_list

    def update(
        self,
        data: pd.DataFrame,
        update_posterior: bool = True,
        update_hyperparam: bool = False,
        use_data: bool = False,
        request_id: int = None,
    ) -> tuple[bool, str, int, dict, int, list, int]:
        """
        Update algorithm
        :param update_posterior: whether to update the posterior or not
        :param update_hyperparam: whether to update the hyperparameters or not
        :param data: data to update algorithm
        :param use_data: whether to use data or not, or use the user_data
        :return: True if algorithm is updated, False otherwise
        :return: error message if algorithm is not updated, None otherwise
        :return: policy id
        :return: algorithm parameters
        :return: error code
        :return: list of users whose posteriors were updated
        :return: last hyperparam update id
        """
        # TODO: Update just using the data in the dataframe

        # Check for dataframe columns
        if use_data:
            try:
                raise NotImplementedError("use_data is not implemented yet")
            except Exception as e:
                return False, "use_data is not implemented yet", self.policyid, {}, 405, [], None

        # Check whether to update the hyperparameters or not
        if update_hyperparam:
            try:
                self.update_hyperparameters(request_id=request_id, data=data, use_data=use_data)
                self.logger.debug("Hyperparameters computed and staged for update with request id: {}".format(request_id))
            except Exception as e:
                if self.debug:
                    self.logger.error(
                        f"[{self.current_study_decision_point}] Error while updating hyperparameters: {e}"
                    )
                    # Log traceback
                    self.logger.error(traceback.format_exc())
                message = "Error while updating hyperparameters"
                return False, message, self.policyid, {}, 403, [], None

        # Check whether to update the posterior or not
        if update_posterior:
            try:
                self.update_posteriors(data, use_data)
                # Update the current policyid
                self.policyid += 1
                self.logger.debug("Posteriors updated")
            except Exception as e:
                if self.debug:
                    self.logger.error(
                        f"[{self.current_study_decision_point}] Error while updating posteriors: {e}"
                    )
                    # Log traceback
                    self.logger.error(traceback.format_exc())
                message = "Error while updating posteriors"
                return False, message, self.policyid, {}, 404, [], self.last_hyperparam_update_id

        # Return the parameters
        try:
            return_dict = {
                "posterior_mean_array": self.posterior_mean.tolist(),
                "posterior_var_array": self.posterior_cov.tolist(),
                "posterior_theta_pop_mean_array": self.theta_pop_mean.tolist(),
                "posterior_theta_pop_var_array": self.theta_pop_cov.tolist(),
                "noise_var": self.noise_var,
                "random_eff_cov_array": self.sigma_u.tolist(),
            }
        except Exception as e:
            if self.debug:
                self.logger.error(
                    f"[{self.current_study_decision_point}] Error while constructing return parameters after RL update: {e}"
                )
                # Log traceback
                self.logger.error(traceback.format_exc())
            message = "Error while returning parameters"
            return False, message, self.policyid, {}, 406, [], self.last_hyperparam_update_id

        return True, None, self.policyid, return_dict, None, self.last_update_users_list, self.last_hyperparam_update_id

    @staticmethod
    def make_state(params: dict) -> list:
        """
        Make state from parameters
        :param params: parameters
        :return: state
        """

        if "engagement_data" not in params:
            raise ValueError("engagement_data not in params")
        if not isinstance(params["engagement_data"], list) and not isinstance(
            params["engagement_data"], np.ndarray
        ):
            raise ValueError("engagement_data is not a list")
        if "recent_cannabis_use" not in params:
            raise ValueError("recent_cannabis_use not in params")
        if "reward" not in params:
            raise ValueError("reward not in params")
        if "time_of_day" not in params:
            raise ValueError("time_of_day not in params")

        if "cannabis_use_data" not in params:
            raise ValueError("cannabis_use_data not in params")

        engagement_data = params["engagement_data"]
        recent_cannabis_use = np.array(params["recent_cannabis_use"])
        reward = params["reward"]
        time_of_day = params["time_of_day"]

        # TODO: Change based on 12/24 hour weighted avg.
        # cannabis_use_data = params["cannabis_use_data"]

        # print("engagement_data", engagement_data)
        # print("recent_cannabis_use", recent_cannabis_use)

        average_reward = np.mean([*engagement_data[-2:], reward])

        # create S1
        if average_reward >= 2:
            S1 = 1
        else:
            S1 = 0

        # create S2 based on time of day
        S2 = time_of_day

        # TODO: Change this to hourly timings
        if recent_cannabis_use.size == 0:
            S3 = 0
        elif np.any(recent_cannabis_use != 0):
            S3 = 0
        elif np.all(recent_cannabis_use == 0):
            S3 = 1

        return [S1, S2, S3]

    @staticmethod
    def make_reward(params: dict) -> float:
        """
        Make reward from parameters
        :param params: parameters
        :return: reward
        """
        param_keys = params.keys()

        if "user_finished_ema" not in param_keys:
            raise ValueError("user_finished_ema not in params")
        if "used_app" not in param_keys:
            raise ValueError("used_app not in params")
        if "activity_response" not in param_keys:
            raise ValueError("activity_response not in params")

        reward = 0

        if params["user_finished_ema"]:
            if params["activity_response"]:
                reward = 3
            else:
                reward = 2
        elif params["used_app"]:
            reward = 1
        return reward

    def update_design_row(
        self,
        user_id: str,
        state: list,
        action: int,
        act_prob: float,
        reward: float,
        decision_index: int,
    ) -> None:
        """
        Update the design row for a given user
        :param state: state of the user
        :param action: action of the user
        :param act_prob: action probability of the user
        :param reward: reward of the user for the LAST time step
        :param decision_index: decision index of the user
        :return: None
        """

        # Get the state, action, and action probability
        if user_id not in self.user_list:
            self.user_list.append(user_id)
            self.num_users += 1
            self.user_data[user_id] = {
                "state": [[], state],
                "action": [None, action],
                "act_prob": [None, act_prob],
                "reward": [reward],
                "design_state": [None],
            }
        else:
            self.user_data[user_id]["state"].append(state)
            self.user_data[user_id]["action"].append(action)
            self.user_data[user_id]["act_prob"].append(act_prob)
            # The reward is updated for the last decision point
            self.user_data[user_id]["reward"].append(reward)

        # Get the individual state elements
        s1 = state[0]
        s2 = state[1]
        s3 = state[2]

        # Create the baseline and advantage
        baseline = [1, s1, s2, s3, s1 * s2, s1 * s3, s2 * s3, s1 * s2 * s3]
        act_advantage = [(act_prob * i) for i in baseline]
        a_pi_advantage = [((action - act_prob) * i) for i in baseline]

        # Create the design row
        design_row = [
            *baseline,
            *act_advantage,
            *a_pi_advantage,
        ]

        # Log event to logger
        if self.debug:
            self.logger.debug(
                "Updating design row for user: {}, state: {}, action: {}, act_prob: {}, decision_index: {}".format(
                    user_id, state, action, act_prob, decision_index
                )
            )

        # return design_row
        self.user_data[user_id]["design_state"].append(design_row)

    def get_policyid(self) -> int:
        """
        Get policy id
        This is used to check if the algorithm has been updated
        Only used for testing
        :return: policy id
        """
        return self.policyid
