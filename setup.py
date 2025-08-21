from setuptools import setup, find_packages

setup(
    name="shapeio",
    version="0.5.0b0",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    author="Peter Grønbæk Andersen",
    author_email="peter@grnbk.io",
    description="A library that provides functions to decode MSTS/ORTS shape files into Python objects and to encode them back into the shape file format.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pgroenbaek/shapeio",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
