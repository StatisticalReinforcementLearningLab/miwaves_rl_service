# src/algorithm/base.py

# Imports
from abc import ABC, abstractmethod


# Create RL algorithm abstract class
class RLAlgorithm(ABC):
    ''' Abstract class for RL algorithm '''

    @abstractmethod
    def __init__(self, nusers):
        pass

    @abstractmethod
    def get_action(self, user_id, state, decision_time):
        pass

    @abstractmethod
    def update(self, data):
        pass
    
    @staticmethod
    @abstractmethod
    def make_state(params):
        pass

    @staticmethod
    @abstractmethod
    def make_reward(params):
        pass