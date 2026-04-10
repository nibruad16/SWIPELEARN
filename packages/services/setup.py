from setuptools import setup, find_packages

setup(
    name="swipelearn-services",
    version="1.0.0",
    description="Business logic services for SwipeLearn",
    packages=find_packages(),
    install_requires=[
        "swipelearn-core",
        "httpx>=0.27.0",
        "beautifulsoup4>=4.12.3",
        "readability-lxml>=0.8.1",
        "lxml>=5.2.2",
        "openai>=1.40.0",
        "feedparser>=6.0.11",
        "supabase>=2.7.0",
    ],
    python_requires=">=3.12",
)
