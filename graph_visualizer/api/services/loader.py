from abc import abstractmethod

from api.services.service_base import ServiceBase

class BaseLoader(ServiceBase):
    """
    Abstract base class for all Data Source plugins.

    Each loader is responsible for parsing a file and constructing a graph.
    """
    @abstractmethod
    def load_file(self, file_name, unique_key=None):
        """
        Parses the file and returns a raw intermediate structure.

        Args:
            file_name: the file-like object to parse
            unique_key: optional key used for identifying nodes

        Returns:
            Raw intermediate data used to build a graph
        """
        pass

    @abstractmethod
    def make_graph(self, tree):
        """
        Builds a graph structure from raw data parsed in `load_file`.

        Args:
            tree: raw structure returned by load_file

        Returns:
            Graph instance representing the data.
        """
        pass
