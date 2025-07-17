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

from api.views import expand_node_view, index_view, upload_file
from api.views import choose_visualizer, complex_visualization, index_view, simple_visualization, upload_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'), 
    path('upload/', upload_file, name='upload_file'),
    path('expand_node', expand_node_view, name='expand_node'),
    path('choose_visualizer/', choose_visualizer, name='choose_visualizer'),
    path('simple_visualization/', simple_visualization, name='simple_visualization'),
    path('complex_visualization/', complex_visualization)
]
