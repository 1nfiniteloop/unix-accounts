from setuptools import setup, find_packages
import pathlib

# Reference: https://packaging.python.org/guides/distributing-packages-using-setuptools

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="unix-accounts",
    version="1.0.0",
    description="Minimal and user-friendly database for sharing unix accounts between computers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1nfiniteloop/unix-accounts",
    author="Lars Gunnarsson",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "SQLAlchemy>=1.4",
        "terminaltables>=3.1",
        "tornado>=6.1"
    ],
    entry_points={
        "console_scripts": [
            "unix-accounts-server=unix_accounts.bin.server:main",
            "unix-accounts=unix_accounts.bin.cli:main",
        ],
    },
)
