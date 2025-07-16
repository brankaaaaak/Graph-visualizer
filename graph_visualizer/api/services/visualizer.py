from abc import abstractmethod

from api.services.service_base import ServiceBase

class BaseVisualizer(ServiceBase):
    @abstractmethod
    def visualize(self, graph, request):
        pass
