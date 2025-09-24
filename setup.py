#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System Setup Script
에너지 관리 시스템 설치 스크립트
"""

from setuptools import setup, find_packages
import os

# README 파일 읽기
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Energy Management System"

# requirements.txt 파일 읽기
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="energy-management-system",
    version="1.0.0",
    author="Energy Team",
    author_email="energy@company.com",
    description="AI-powered Energy Management System with IoT Integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/energy-management-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "energy-dashboard=app:main",
            "energy-collector=scripts.data_collector:main",
            "energy-preprocessor=scripts.data_preprocessor:main",
            "energy-trainer=scripts.ml_model_developer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.csv", "*.pkl", "*.html", "*.css", "*.js"],
    },
    zip_safe=False,
)
