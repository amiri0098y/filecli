from setuptools import setup

setup(
    name="file-cli",
    version="0.1",
    py_modules=["ftp_cli"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "filec=ftp_cli:main",
        ],
    },
    author="Duck",
    description="Hi bros,this is a file manager in cli",
)
