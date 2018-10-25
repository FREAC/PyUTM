import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyutm",
    version="0.1.5",
    author="Philip Griffith",
    author_email="philip.griffith@fsu.edu",
    description="Creates standardized grid references and unique identifiers for point data.",
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
