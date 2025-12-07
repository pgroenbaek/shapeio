from setuptools import setup, find_packages

setup(
    name="shapeio",
    version="0.5.0b3",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    author="Peter Grønbæk Andersen",
    author_email="peter@grnbk.io",
    description="A Python module to read MSTS/ORTS shape files into Python data structures and write them back to text.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "Homepage": "https://github.com/pgroenbaek/shapeio",
        "Issues": "https://github.com/pgroenbaek/shapeio/issues",
        "Source": "https://github.com/pgroenbaek/shapeio",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
