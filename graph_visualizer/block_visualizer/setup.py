from setuptools import setup, find_packages

setup(
    name='block-visualizer',
    version='0.1.0',
    description='Block graph visualizer plugin for Django',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.visualizer"],
    entry_points={
        'visualizer':
        ['block-visualizer=plugin.visualizer.block_visualizer:BlockVisualizer']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
