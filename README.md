# Graph-visualizer
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.x-blueviolet)](https://www.djangoproject.com/)

Graph Visualizer is a Django-based web platform for visualizing and interacting with graph data.  
It supports pluggable data source parsers (loaders) and graph visualizers, offering a flexible and extensible architecture.

---

## 📌 Features

- 🔌 Plugin-based architecture for data sources and visualizations
- 📁 Support for multiple graph formats (JSON, XML, File System)
- 📊 Interactive graph visualization using D3.js
- 🌲 Tree View for exploring hierarchy
- 🧠 Workspace management (multiple graphs with filters and search)
- 🎯 Graph editing via terminal commands (add/edit/delete nodes & edges)
- 🔎 Zoom, pan, drag-and-drop, and node mouseover interactions
- 🔄 Reset & filter functionality
- 🧩 Easily extendable with custom loaders and visualizers

---

## 🚀 Getting Started
Open terminal

### 1. Create a virtual environment and activate it
```bash
python -m venv venv
venv\Scripts\activate #on Windows
```
### 2. Install Django and all plugin dependencies
From the root of the project, run:

```bash
pip install django
pip install setuptools
pip install rdflib
cd xml_loader
python setup.py install
cd ..
cd json_loader
python setup.py install
cd ..
<<<<<<< HEAD
<<<<<<< HEAD
cd rdf_loader
=======
cd fs_loader
>>>>>>> d98c78006967f7f5e89ea247a0bc7725cf3b950a
=======
cd rdf_loader
python setup.py install
cd ..
cd fs_loader
>>>>>>> 1308c0d92cc065c4db3ec1492c284422208e97f3
python setup.py install
cd ..
cd simple_visualizer
python setup.py install
cd ..
cd block_visualizer
python setup.py install
cd ..
```
### 3. Run the Django server
```bash
python manage.py runserver
```

Then open your browser and navigate to:
📍 http://127.0.0.1:8000/

---

🧩 Plugin System
Each plugin must implement a class that inherits from BaseLoader or BaseVisualizer (from the api package) and be installed into the environment!
