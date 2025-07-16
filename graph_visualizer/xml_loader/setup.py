from setuptools import setup, find_packages

setup(
    name='xml_loader',
    version='0.2',
    description='Plugin for loading graphs from XML files',
    author='Anđela Voštić',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.loader"],
    entry_points={
        "loader": 
        ["xml-loader=plugin.loader.xml_loader:XmlLoader"]
    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)
