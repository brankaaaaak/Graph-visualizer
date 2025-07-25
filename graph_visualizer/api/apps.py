from django.apps import AppConfig
import pkg_resources

from api.models import Tree, TreeNode
from graph_platform.core import state

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        state.ready()