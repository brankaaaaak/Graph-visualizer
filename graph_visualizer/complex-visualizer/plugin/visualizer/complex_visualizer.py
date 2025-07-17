from api.services.visualizer import BaseVisualizer


class ComplexVisualizer(BaseVisualizer):
    def identifier(self):
        return "complex-visualizer"

    def name(self):
        return "Complex View"