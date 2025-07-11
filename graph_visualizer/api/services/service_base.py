from abc import ABC, abstractmethod


class ServiceBase(ABC):
    @abstractmethod
    def identifier(self):
        pass
    
    @abstractmethod
    def name(self):
        pass