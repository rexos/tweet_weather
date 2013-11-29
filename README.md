WeatherTweet
===========

Python module which highlights correlations between the weather and a sentiment analysis of tweets. Results are displayed through a local web page powered by Flask.

Installation
===========

The installation should provide all required packages
-> python setup.py install

Running
===========
Running the server will allow the access to http://localhost:5000
From there, all pages can be accessed and the data mining thread must be launched (and stopped) from within the web interface.
-> cd server
-> python server.py


Testing
===========

Testing is powered by py.test and can be done at the root with
-> python setup.py test
