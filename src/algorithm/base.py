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
    def get_action(self, user, state):
        pass

    @abstractmethod
    def update(self, state, action, reward, next_state):
        pass