import sys
from flask import Flask, render_template
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from pysqlite2 import dbapi2 as db
import gevent
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

PORT = 5000

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

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/new_posts': BaseNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

if __name__ == '__main__':
	# app.run()
	server = SocketIOServer(('', PORT), app, resource="socket.io")
	twThread = TweetWeather(server, name = "Tweet-Weather-Thread")
	gevent.spawn(twThread.new_post,server)
	twThread.start()
	try:
		server.serve_forever()
	except KeyboardInterrupt:
	    twThread.stop()
	    server.stop()
	    sys.exit()
