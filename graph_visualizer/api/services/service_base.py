from abc import ABC, abstractmethod

class ServiceBase(ABC):
    """
    Abstract base interface for all plugin components in the system.

    All plugins (like loaders and visualizers) must implement:
    - `identifier()`: unique string identifier.
    - `name()`: human-readable name.
    """
    @abstractmethod
    def identifier(self):
        """Returns unique string identifier of the plugin (e.g. 'json-loader')."""
        pass
    
    @abstractmethod
    def name(self):
        """Returns human-readable name of the plugin (e.g. 'JSON Loader')."""
        pass

