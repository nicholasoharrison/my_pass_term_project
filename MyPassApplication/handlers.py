
from abc import ABC, abstractmethod





# Chain of Responsibility Implementation --------------------------------------------------------
class SecurityQuestionHandler(ABC):
    def __init__(self):
        self._next_handler = None # holds the next handler in the chain of responsibility

    # sets the next handle to the desired handler
    def set_next(self, handler):
        self._next_handler = handler
        return handler

    # the handling of each class will be implemented by the subclases according to the needs of the program
    @abstractmethod
    def handle(self, user, answer):
        pass

class Question1Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q1Answer: # checks if the provided answer matches the users first security question
            if self._next_handler: # if there is another handler, this sets the next handler to that next handler
                return self._next_handler.handle(user, answer)
            return True
        return False

class Question2Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q2Answer: # checks if the provided answer matches the users second security question
            if self._next_handler: # if there is another handler, this sets the next handler to that next handler
                return self._next_handler.handle(user, answer)
            return True
        return False

class Question3Handler(SecurityQuestionHandler):
    def handle(self, user, answer):
        if answer == user.security_question.q3Answer: # checks if the provided answer matches the users third security question
            return True # no more handling will be done if it gets handled as true through the third handler
        return False
# End of Chain of Responsibility Implementation --------------------------------------------------------