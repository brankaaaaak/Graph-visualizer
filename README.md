# Graph-visualizer
Graph Visualizer is a Django-based web platform for visualizing and interacting with graph data.  
It supports pluggable data source parsers (loaders) and graph visualizers, offering a flexible and extensible architecture.

---

## 📌 Features

- 🔌 Plugin-based architecture for data sources and visualizations
- 📁 Support for multiple graph formats (JSON, XML)
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

pip install django
cd xml_loader
python setup.py install
cd ..
cd json_loader
python setup.py install
cd ..
cd simple_visualizer
python setup.py install
cd ..
cd block_visualizer
python setup.py install
cd ..

### 3. Run the Django server
python manage.py runserver

Then open your browser and navigate to:
📍 http://127.0.0.1:8000/

---

🧩 Plugin System
Each plugin must implement a class that inherits from BaseLoader or BaseVisualizer (from the api package) and be installed into the environment!
