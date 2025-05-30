from abc import ABC, abstractmethod
from typing import List


class IUserInterface(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def send_message(self, chat_id: str, text: str):
        pass

    @abstractmethod
    def ask_question(self, chat_id: str, question: str, options: List[str] = None):
        pass
