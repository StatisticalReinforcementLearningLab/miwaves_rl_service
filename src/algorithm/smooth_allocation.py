import numpy as np
import pickle as pkl
import scipy.special as special
from typing import Callable
import scipy.stats as stats

def load_random_vars(path) -> np.array:
    # Load random variables - normal with mean 0 and var 1
    with open(path, "rb") as f:
        random_vars = pkl.load(f)

    return random_vars

def get_allocation_function(
    func_type: str,
    B: float,
    randomvars: np.array,
    C: float = 5.0,
    L_min: float = 0.2,
    L_max: float = 0.8,
) -> Callable:
    """
    Gets the allocation function to be used for the run
    """

    def thompson_sampling(mean: float, var: float) -> float:
        """
        Simple thompson sampling allocation function
        """
        prob = 1 - stats.norm.cdf(0, mean, np.sqrt(var))
        return prob

    def logistic_function_infinity(x: float) -> float:
        if x >= 0:
            return L_max
        else:
            return L_min

    def smooth_posterior_sampling_inf(mean: float, var: float) -> float:
        std = np.sqrt(var)
        samples = mean + (randomvars * std)
        prob = np.mean([logistic_function_infinity(i) for i in samples])

        return prob

    def logistic_function(x: float) -> float:
        numerator = L_max - L_min
        denominator_inverse = special.expit(B * x - np.log(C))
        return L_min + numerator * denominator_inverse

    def smooth_posterior_sampling(mean: float, var: float) -> float:
        std = np.sqrt(var)
        samples = mean + (randomvars * std)
        prob = np.mean(logistic_function(samples))

        # prob = stats.norm.expect(func=logistic_function, loc=mean, scale=np.sqrt(var))
        return prob

    if func_type == "thompson":
        return thompson_sampling
    elif func_type == "smooth":
        if np.isinf(B):
            return smooth_posterior_sampling_inf
        else:
            return smooth_posterior_sampling
    else:
        raise NotImplementedError
