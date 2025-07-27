from abc import abstractmethod

from api.services.service_base import ServiceBase

class BaseVisualizer(ServiceBase):
    """
    Abstract base class for all Visualizer plugins.

    Visualizers are responsible for rendering a Graph into an HTML view using D3.js and Django templates.
    """
    @abstractmethod
    def visualize(self, graph, request):
        """
        Generates HTML visualization for the given graph.

        Args:
            graph: Graph instance to visualize
            request: Django HttpRequest, used for context or user input

        Returns:
            Rendered HTML snippet (string) to be injected in template.
        """
        pass
