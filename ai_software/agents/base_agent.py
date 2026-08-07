from abc import ABC, abstractmethod

from logger import get_logger


class BaseAgent(ABC):
    def __init__(self, llm):
        self.llm = llm
        self.log = get_logger(self.__class__.__name__)

    @abstractmethod
    def run(self, state):
        pass