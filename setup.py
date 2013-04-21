import os
from setuptools import setup

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

setup(name="elephant_backup",
      version="0.1",
      description="Simple and easy framework for writing backup scripts",
      long_description=read_file("README.rst"),
      author="Mark Embling",
      author_email="contact@markembling.info",
      url="http://github.com/markembling/elephant",
      licence="BSD",
      py_modules=["elephant_backup"],
      install_requires=["boto"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: BSD License",
          "Topic :: System :: Archiving :: Backup"
      ])
