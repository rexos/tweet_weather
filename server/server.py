"""
server.py is a python module which implements a flask http
server needed by the whole web application.
"""

import sys
from flask import Flask, render_template, jsonify
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from pysqlite2 import dbapi2 as db
import gevent
import os
from analysis import Analyzer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from cStringIO import StringIO
import urllib
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
    data = []
    if os.path.exists('data.sqlite'):
        cur = db.connect('data.sqlite').cursor()
        cur.execute('SELECT id,sentimentValue,weather,infos FROM tweets ORDER BY id DESC')
        data = cur.fetchall()
    return render_template('list.html', data=data)

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/new_posts': BaseNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

def check_conn():
    """
    Checks whether a working Internet connection exists
    """
    try:
        urllib.urlopen( 'http://google.com' )
        return True
    except:
        pass
    return False

@app.route('/start')
def start():
    if check_conn():
        twThread.start()
        return jsonify('true')
    else:
        twThread.connexion_lost("Absent Internet Access")
        return jsonify('false')

@app.route('/stop')
def stop():
    twThread.stop()
    return jsonify('true')

@app.route("/plot")
def plot():
    if os.path.exists('data.sqlite'):
        cur = db.connect('data.sqlite').cursor()
        cur.execute('SELECT sentimentValue, weatherValue FROM tweets'
                    ' WHERE sentimentValue > 0 ORDER BY id DESC')
        data = cur.fetchall()

    x = [point[0] for point in data]
    y = [point[1] for point in data]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = np.linspace(0, 1, 1000)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.plot(xs, xs, label='Perfect Correlation', color='green')
    ax.scatter(x, y, label='Data Points', color='red')
    ax.legend()

    io = StringIO()
    fig.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    return render_template('plot.html', data=data)

if __name__ == '__main__':
    analyzer = Analyzer()
    server = SocketIOServer(('', PORT), app, resource="socket.io")
    twThread = TweetWeather(server, analyzer, name = "Tweet-Weather-Thread")
    gevent.spawn(twThread.new_post, server)
    gevent.spawn(twThread.connexion_lost, server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        twThread.stop()
        server.stop()
        sys.exit()
