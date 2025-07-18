from setuptools import setup, find_packages

setup(
    name='simple-visualizer',
    version='0.2.0',
    description='Simple graph visualizer plugin for Django',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.visualizer"],
    entry_points={
        'visualizer':
        ['simple-visualizer=plugin.visualizer.simple_visualizer:SimpleVisualizer']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
