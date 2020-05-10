from setuptools import setup

setup(
    name="monkey",
    version="0.1.0",
    author="Jack evans",
    author_email="jack@evans.gb.net",
    description="Python implementation of the Monkey programming language",
    entry_points={
        "console_scripts": ["monkey=monkey.monkey:main"]
    }
)
