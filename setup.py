"""Setup script for ExplainStack."""

from setuptools import setup, find_packages

setup(
    name="explainstack",
    version="1.0.0",
    description="Multi-agent AI system for OpenStack development",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "chainlit",
        "openai",
        "python-dotenv",
        "requests",
        "anthropic",
        "google-generativeai",
    ],
    entry_points={
        "console_scripts": [
            "explainstack=explainstack.cli.main:main",
        ],
    },
)
