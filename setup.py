import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'pyutm', '__version__.py')) as fp:
    exec(fp.read(), version)

setuptools.setup(
    name="pyutm",
    version=version['__version__'],
    author="Philip Griffith",
    author_email="philip.griffith@fsu.edu",
    description="Creates standardized grid references, unique identifiers and UTM coordinates for point data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FREAC/pyutm",
    packages=setuptools.find_packages(exclude=['docs', 'tests']),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'pandas',
        'pyshp',
        'pyproj'
    ]
)
