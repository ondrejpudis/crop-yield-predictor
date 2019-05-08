import os

from setuptools import find_packages, setup

with open("requirements.in") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]

setup(
    name="op-yield-predictor",
    version=os.getenv("PACKAGE_VERSION") or "dev",
    author="Ondrej Pudiš",
    author_email="pudisond@fit.cvut.cz",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points="""
        [console_scripts]
        test-predict=src.cli:test
        predict=src.cli:predict
    """,
)
