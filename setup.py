#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="radioforms",
    version="0.1.0",
    description="ICS Forms Management Application",
    author="RadioForms Team",
    author_email="example@example.com",
    url="https://github.com/yourusername/radioforms",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySide6>=6.0.0",
        "reportlab>=3.6.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Desktop Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
    ],
    entry_points={
        "console_scripts": [
            "radioforms=radioforms.main:main",
        ],
    },
    python_requires=">=3.10",
)
