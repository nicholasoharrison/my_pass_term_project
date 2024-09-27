
from abc import ABC, abstractmethod





# Chain of Responsibility Implementation --------------------------------------------------------
class SecurityQuestionHandler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, user, answer):
        pass

class Question1Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q1Answer:
            if self._next_handler:
                return self._next_handler.handle(user, answer)
            return True
        return False

class Question2Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q2Answer:
            if self._next_handler:
                return self._next_handler.handle(user, answer)
            return True
        return False

class Question3Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q3Answer:
            return True
        return False
# End of Chain of Responsibility Implementation --------------------------------------------------------