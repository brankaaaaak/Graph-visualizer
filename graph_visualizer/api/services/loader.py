from abc import abstractmethod

from api.services.service_base import ServiceBase

class BaseLoader(ServiceBase):
    @abstractmethod
    def load_file(self, file_name, unique_key=None):
        pass

    @abstractmethod
    def make_graph(self, tree):
        pass
