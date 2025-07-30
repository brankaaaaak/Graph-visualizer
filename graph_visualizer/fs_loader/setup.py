from setuptools import setup, find_packages

setup(
    name='fs_loader',
    version='0.2',
    description='Plugin for loading graphs from file system structure',
    author='Ana Krunić',
    packages=find_packages(),
    namespace_packages=["plugin", "plugin.loader"],
    entry_points={
        "loader": [
            "fs-loader=plugin.loader.fs_loader:FileSystemLoader"
        ]
    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)
