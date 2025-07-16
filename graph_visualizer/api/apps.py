from django.apps import AppConfig
import pkg_resources


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    loaders = []
    visualizers = []

    def ready(self):
        self.loaders = load_plugins("loader")
        self.visualizers = load_plugins("visualizer")
        print(len(self.loaders))
        print(len(self.visualizers))
    
    def get_loader(self, id):
        print(id)
        for loader in self.loaders:
            print(loader.identifier())
            if loader.identifier() == id:
                return loader
        return None

    def get_visualizer(self, id):
        print(id)
        for visualizer in self.visualizers:
            print(visualizer.identifier())
            if visualizer.identifier() == id:
                return visualizer
        return None

def load_plugins(entry_point):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=entry_point):
        print(ep)
        p = ep.load()
        plugin = p()
        plugins.append(plugin)
    return plugins