from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import sys

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "WeatherTweet",
    version = "0.1",
    packages = find_packages(),
    scripts = ['server/server.py','server/tweetweather.py','server/analysis.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3'],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Alex Pellegrini, Woody Rousseau",
    author_email = "wrousseau@ensta.fr",
    description = "Tweets and Weather Data Mining to find correlation between the weather and a tweets sentiment analysis",
    license = "GPL",
    keywords = "twitter sentiment analysis weather",

    # could also include long_description, download_url, classifiers, etc.
)
