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
def home():
	return render_template('hello.html')

@app.route('/list_data')
def list_data():
	cur = db.connect('data.sqlite').cursor()
	cur.execute('SELECT * FROM tweets ORDER BY id DESC')
	data = cur.fetchall()
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
