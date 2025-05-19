from setuptools import setup

setup(
    name="file-cli",
    version="0.1",
    py_modules=["main"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "filec=main:main",
        ],
    },
    author="Duck",
    description="Hi bros,this is a file manager in cli",
)
