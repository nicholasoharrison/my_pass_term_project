
class Observer:    
    #Base class for all observers in the Observer pattern.Observers must implement the `update` method.    
    def update(self, event, data):
        raise NotImplementedError("Subclasses must implement the `update` method")


class ObserverRegistry:
    _observers = {}

    @classmethod
    def register_observer(cls, event, observer):
              # Register an observer for a specific event.
        if event not in cls._observers:
            cls._observers[event] = []
        cls._observers[event].append(observer)

    @classmethod
    def notify_observers(cls, event, data):
        #        Notify all observers of a specific event.      
        if event in cls._observers:
            for observer in cls._observers[event]:
                observer.update(event, data)