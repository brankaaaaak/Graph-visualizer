"""
URL configuration for graph_visualizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import clear_graph, create_edge, create_node, delete_edge, delete_node, edit_edge, edit_node, expand_node_from_view, expand_node_view, filter_view, index_view, reset_graph, search, upload_file,visualize
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'), 
    path('upload/', upload_file, name='upload_file'),
    path('expand_node/', expand_node_view, name='expand_node'),
    path('visualize/', visualize, name='visualize'),
    path('expand/<int:node_id>/', expand_node_from_view, name='expand_node_from_view'),
    path("api/create_node/", create_node, name="create_node"),
    path("api/create_edge/", create_edge, name="create_edge"),
    path('api/delete_node/', delete_node, name='delete_node'),
    path('api/delete_edge/', delete_edge, name='delete_edge'),
    path('api/edit_node/', edit_node, name='edit_node'),
    path('api/edit_edge/', edit_edge, name='edit_edge'),
    path("api/search/", search, name="search"),
    path('api/clear/', clear_graph, name='clear_graph'),
    path('api/filter/',filter_view,name="filter_view"),
    path('api/reset_graph/',reset_graph,name="reset_graph")
]
