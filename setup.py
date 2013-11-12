import os
from setuptools import setup, find_packages

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
