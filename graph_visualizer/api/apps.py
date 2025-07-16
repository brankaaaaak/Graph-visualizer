from django.apps import AppConfig
import pkg_resources


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    loaders = []
    visualizers = []
    graph= None
    visualizer=None
    loader=None

    def ready(self):
        self.loaders = load_plugins("loader")
        self.visualizers = load_plugins("visualizer")
        print(len(self.loaders))
        print(len(self.visualizers))

def load_plugins(entry_point):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=entry_point):
        print(ep)
        p = ep.load()
        plugin = p()
        plugins.append(plugin)
    return plugins
