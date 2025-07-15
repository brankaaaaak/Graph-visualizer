from api.services.visualizer import BaseVisualizer


class SimpleVisualizer(BaseVisualizer):
    def identifier(self):
        return "simple-visualizer"

    def name(self):
        return "Simple View"