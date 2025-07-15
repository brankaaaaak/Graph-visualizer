from setuptools import setup, find_packages

setup(
    name='json_loader',
    version='0.1.0',
    description='Plugin for loading graphs from JSON files',
    author='Branka Kovačević',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.loader"],
    entry_points={
        "loader": 
        ["json-loader=plugin.loader.json_loader:JsonLoader"]
    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)