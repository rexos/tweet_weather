import sys
from flask import Flask, render_template
from pysqlite2 import dbapi2 as db
import threading
from numpy import arange
import nltk
import os
import time
import matplotlib.pyplot as plt
import simplejson as jsn
from tweetweather import TweetWeather

path = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(path)

app = Flask(__name__)

@app.route('/')
@app.route('/<name>')
def home(name=None):
	values = [ 0,1,2,3,4,5 ]
	return render_template('hello.html',name=name, values=values)

@app.route('/list_data')
def list_data():
	cur = db.connect('data.sqlite').cursor()
	data = cur.execute('SELECT * FROM tweets').fetchall()
	return render_template('list.html', data=data)

if __name__ == '__main__':
	twThread = TweetWeather(name = "Tweet-Weather-Thread")
	twThread.start()
	app.run()
	while True:
	    try:
	        time.sleep(.3)
	    except KeyboardInterrupt:
	        twThread.stop()
	        sys.exit()
