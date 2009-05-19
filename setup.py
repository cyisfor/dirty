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
    version="1.0.2",
    description="A dirty and simple HTML/XML template engine for Python 3.",
    long_description="Dirty is a simple internal DSL template library that"
                     "helps you to write some HTML or XML markup with Python."
                     "It is inspired by Markaby.",
    author="Hong, MinHee",
    author_email="minhee@dahlia.kr",
    url="http://dirty.googlecode.com/",
    packages=["dirty"],
    package_dir=dict(dirty="dirty"),
    cmdclass=dict(test=TestCommand),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
            "GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: "
            "CGI Tools/Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML"
    ]
)

