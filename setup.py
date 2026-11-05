# setup.py
from setuptools import setup, find_packages

setup(
    name="creditpulse_ai_workstation",
    version="1.0.0",
    description="Enterprise Multi-Product Retail Ledger Analytics Workstation & Risk Compliance Framework",
    long_description_content_type="text/markdown",
    author="T A Srinivas",
    author_email="tasrinivass@gmail.com",
    url="https://github.com",
    license="MIT",
    packages=find_packages(exclude=["tests*", "docs*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.35.0",
        "pandas>=2.0.0",
        "plotly>=5.20.0",
        "reportlab>=4.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    keywords="accounting-engine analytics-dashboard automated-testing financial-engineering risk-management",
)
