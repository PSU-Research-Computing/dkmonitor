"""
Setup script
"""
from setuptools import setup, find_packages

long_description = "open file here"

setup(name="dbtracker",
      version="1.0.0",
      description="Monitors specified disks or directories for user and general stats",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      install_requires=["psycopg2"],
      long_description=long_description,
      entry_points={"console_scripts": ["dkmonitor=dkmonitor.monitor_manager:main"],}) #Could use some more thought
