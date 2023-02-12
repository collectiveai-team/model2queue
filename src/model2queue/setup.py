from setuptools import setup, find_packages

setup(
    name="model2queue",
    packages=find_packages(),
    version="0.1.0",
    description="A library to expose an api with a queue for batch predictions",
    author="collective.ai",
    author_email="team.collective.ai@gmail.com",
    url="git repo url to clone it",
    install_requires=["kombu", "fastapi", "uvicorn"],
    package_data={"": ["*.yml", "*.yaml"]},
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)