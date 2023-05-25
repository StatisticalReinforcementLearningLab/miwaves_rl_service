# src/algorithm/flat_prob.py

# Imports
import numpy as np
from src.algorithm.base import RLAlgorithm

class FlatProbabilityAlgorithm(RLAlgorithm):
    ''' Flat probability algorithm '''

    def __init__(self, nusers: int = 10, prob: float = 0.5) -> None:
        '''
        Initialize flat probability algorithm
        :param prob: probability of taking action
        '''
        self.prob = prob

    def get_action(self, user: int, state: np.ndarray, seed: int = -1) -> tuple:
        '''
        Get action
        :param state: state of the user
        :param seed: seed for random number generator
        :return: action, seed, probability of taking action
        '''

        if seed != -1:
            np.random.seed(seed)
        else:
            # set seed
            np.random.seed()

            # generate seed
            seed = np.random.randint(0, 2**32 - 1)

            # set seed
            np.random.seed(seed)
        
        # get action
        action = np.random.binomial(1, self.prob)

        return action, seed, self.prob

    def update(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        '''
        Update algorithm
        :param state: state of the user
        :param action: action taken
        :param reward: reward received
        :param next_state: next state of the user
        '''
        pass

    @staticmethod
    def make_state(params: dict) -> np.ndarray:
        '''
        Make state from parameters
        :param params: parameters
        :return: state
        '''
        pass

    @staticmethod
    def make_reward(params: dict) -> float:
        '''
        Make reward from parameters
        :param params: parameters
        :return: reward
        '''
        pass