#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webpycalc-ROMAN-SOLOYOUV",
    version="0.0.1",
    author="Roman Soloyouv",
    author_email="solouyv@gmail.com",
    description="Pure-python web or command-line calculator.",
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    url="https://github.com/solouyv/calculator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'webpycalc = webpycalc:main',
            'pycalc = pycalc:main',
        ],
    },
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'flask',
    ],
)
