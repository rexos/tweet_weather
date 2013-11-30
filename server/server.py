"""
server.py is a python module which implements a flask http
server needed by the whole web application.
"""

import sys
from flask import Flask, render_template, jsonify, Response, request
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from pysqlite2 import dbapi2 as db
import gevent
import cProfile
import os
from analysis import Analyzer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from cStringIO import StringIO
import urllib2
from tweetweather import TweetWeather

PATH = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(PATH)

PORT = 5000

app = Flask(__name__)

@app.route('/testing')
def runTest():
    """
    Method used to test
    if the app is running
    """
    return 'Hello World!'

@app.route('/')
def home():
    """
    The home page is a static page
    allowing the choice of the visualization tool
    """
    return render_template('hello.html')


@app.route('/list_data')
def list_data():
    """
    This page displays all objects in a table
    updated as they are mined.
    The user can start and stop the data mining
    using buttons.
    """
    data = []
    if os.path.exists('data.sqlite'):
        cur = db.connect('data.sqlite').cursor()
        cur.execute('SELECT id,sentimentValue,weather,infos FROM tweets ORDER BY id DESC')
        data = cur.fetchall()
    return render_template('list.html', data=data)


@app.route('/map')
def display_map():
    """
    This page displays a map centered around the United States
    containing a weather layer and a heatmap with arriving objects.
    The user can start and stop the data mining
    using buttons.
    """
    return render_template('map.html')


@app.route('/socket.io/<path:remaining>')
def socketio(request):
    """
    This route configures the WebSocket
    used to let the client know that new objects
    were mined
    """
    try:
        socketio_manage(request.environ,
                        {'/new_posts': BaseNamespace},
                        request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()


def check_conn():
    """
    Checks whether a working Internet connection is available
    """
    try:
        urllib2.urlopen('http://74.125.228.100')  # Google IP (no DNS lookup)
        return True
    except urllib2.URLError:
        pass
    return False


@app.route('/start')
def start():
    """
    Starts the data mining thread if an internet connection is available
    """
    if check_conn():
        twThread.start()
        return jsonify('true')
    else:
        twThread.connexion_lost("Absent Internet Access")
        return jsonify('false')


@app.route('/stop')
def stop():
    """
    Stops the data mining thread
    """
    twThread.stop()
    return jsonify('true')


@app.route("/plot")
def plot():
    testing = request.args.get('testing', 0, type=int)
    if os.path.exists('data.sqlite'):
        cur = db.connect('data.sqlite').cursor()
        cur.execute('SELECT sentimentValue, weatherValue FROM tweets'
                    ' WHERE sentimentValue > 0 ORDER BY id DESC')
        all_fetched = cur.fetchall()
        x = [point[0] for point in all_fetched]
        y = [point[1] for point in all_fetched]
    elif testing:
        x = 0.5
        y = 0.3
    else:
        return render_template('500.html', data='Database not found')

    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = np.linspace(0, 1, 1000)
    axis.set_xlim([0, 1])
    axis.set_ylim([0, 1])
    axis.plot(xs, xs, label='Perfect Correlation', color='green')
    axis.scatter(x, y, label='Data Points', color='red')
    plt.xlabel('sentiment')
    plt.ylabel('weather')
    axis.legend()

    str_io = StringIO()
    fig.savefig(str_io, format='png')
    img_data = str_io.getvalue().encode('base64')
    refresh = request.args.get('refresh', 0, type=int)
    if refresh:
        return img_data
    return render_template('plot.html', data=img_data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500



if __name__ == '__main__':
    analyzer = Analyzer()
    server = SocketIOServer(('', PORT), app, resource="socket.io")
    twThread = TweetWeather(server, analyzer, name="Tweet-Weather-Thread")
    twThread.daemon = True
    gevent.spawn(twThread.new_post, server)
    gevent.spawn(twThread.connexion_lost, server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        twThread.stop()
        server.stop()
        sys.exit()
