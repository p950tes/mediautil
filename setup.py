#!/usr/bin/env python3
"""Setup script for mediautil package."""

from setuptools import setup, find_packages

with open("mediautil/__init__.py", "r", encoding="utf-8") as f:
    version = None
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="mediautil",
    version=version or "1.0.0",
    description="Multi-purpose media editing tool",
    author="server1-scripts",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mediautil = mediautil.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
