from abc import (
    ABC,
    abstractmethod
)
import argparse

class Command(ABC):

    @abstractmethod
    def exec(self, args: argparse.Namespace):
        pass
