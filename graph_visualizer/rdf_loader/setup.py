from setuptools import setup, find_packages

setup(
    name='rdf_loader',
    version='0.3',
    description='Plugin for loading graphs from RDF files',
    author='Mina Radenković',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.loader"],
    entry_points={
        "loader":
        ["rdf-loader=plugin.loader.rdf_loader:RDFLoader"]
    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)