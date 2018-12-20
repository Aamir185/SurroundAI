"""
Python package definition for Surround
"""
import os

from setuptools import setup, find_packages


# Collect version from repo tag
VERSION = os.getenv('VERSION_TAG')

setup(name='surround',
      version=VERSION,
      description='Surround is a framework for serving machine learning pipelines in Python.',
      url='http://github.com/dstil/surround',
      author='Scott Barnett',
      author_email='scott.barnett@deakin.edu.au',
      packages=['surround'],
      test_suite="surround.tests",
      zip_safe=False
)
