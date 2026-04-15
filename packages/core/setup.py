from setuptools import setup, find_packages

setup(
    name="swipelearn-core",
    version="1.0.0",
    description="Shared models and schemas for SwipeLearn",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.8.0",
        "pydantic-settings>=2.4.0",
        "email-validator>=2.1.0",   # Required for EmailStr validation
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
        ],
    },
    python_requires=">=3.12",
)
