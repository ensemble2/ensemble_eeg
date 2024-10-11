#!/usr/bin/env python3
# setup.py
import setuptools

setuptools.setup(
    name="ensemble_edf",
    py_modules=["ensemble_edf", "brm_to_edf"],
    python_requires=">3.1",
    install_requires=["defusedxml", "numpy"],
    version="0.1.6",
    author="Bauke van der Velde",
    author_email="b.vandervelde-3@umcutrecht.nl",
    packages=["ensemble_eeg"],
)
