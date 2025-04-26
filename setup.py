from setuptools import setup, find_packages
import os
import codecs

# Get the version from version.py
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'guipysofi', 'version.py'), encoding='utf-8') as f:
    exec(f.read())

# Get the long description from README.md
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="guipysofi",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "tkinterdnd2",
        "matplotlib",
        "numpy",
        "tifffile",
        "pillow",
        "scipy",  # Required for internal implementations
    ],
    extras_require={
        "pysofi": [
            "pysofi",  # Optional but recommended
        ],
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            "sphinx",
            "sphinx_rtd_theme",
        ],
        "performance": [
            "psutil",
            "numba",
        ],
    },
    entry_points={
        "console_scripts": [
            "guipysofi=guipysofi.main:main",
        ],
    },
    author="Colin Galbraith",
    author_email="chmartin@ucsb.edu",
    description="An Open Source Graphical Extension to the PySOFI Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TestaLab/Live_SOFI2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.7",
) 