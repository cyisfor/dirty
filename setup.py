#!/usr/bin/env python
from distutils.core import setup
from distutils.cmd import Command


class TestCommand(Command):
    description = "run unit tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import doctest, dirty
        doctest.testmod(dirty)
        doctest.testmod(dirty.html)
        doctest.testmod(dirty.xml)


setup(
    name="dirty",
    version="1.0.1",
    description="A dirty and simple HTML/XML template engine for Python 3.0",
    author="Hong, MinHee",
    author_email="minhee@dahlia.kr",
    url="http://dirty.googlecode.com/",
    packages=["dirty"],
    package_dir=dict(dirty="dirty"),
    cmdclass=dict(test=TestCommand)
)

