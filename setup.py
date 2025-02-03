from setuptools import setup, find_packages

setup(
    name="plugmini",
    version="1.0.0",
    description="Control SwitchBot Plug Mini over BLE",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ryomashita",
    author_email="86085692+ryomashita@users.noreply.github.com",
    url="https://github.com/ryomashita/plugmini",
    packages=["plugmini"],
    install_requires=[
        "bleak",  # BLE library for Python
        "python-dotenv",  # For loading environment variables from .env file
    ],
    entry_points={
        "console_scripts": [
            "plugmini=plugmini.plugmini:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
