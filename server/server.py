"""
server.py is a python module which implements a flask http
server needed by the whole web application.
"""

import sys
from flask import Flask, render_template, jsonify, Response, request, abort
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from pysqlite2 import dbapi2 as db
import gevent
import os
from analysis import Analyzer
from plotting import ScatterPlot
import urllib2
from tweetweather import TweetWeather

PATH = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(PATH)

PORT = 5000

app = Flask(__name__)


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


@app.route("/plot")
def plot():
    """
    This page displays a scatter plot of all gathered tweets
    The x-axis is the sentiment value.
    The y-axis is the weather value.
    The closer points are to the 'identity' line,
    the closer they fit our hypothesis
    """
    scatterPlot = ScatterPlot(1)
    scatterPlot.set_data()
    img_data = scatterPlot.get_image_data()
    refresh = request.args.get('refresh', 0, type=int)
    if refresh:
        return img_data
    return render_template('plot.html', data=img_data)


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
        tw_thread.start()
        return jsonify('true')
    else:
        tw_thread.connexion_lost("Absent Internet Access")
        return jsonify('false')


@app.route('/stop')
def stop():
    """
    Stops the data mining thread
    """
    tw_thread.stop()
    return jsonify('true')


@app.errorhandler(404)
def page_not_found(exc):
    """
    404 error handler
    used if a non existant route
    is requested
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(exc):
    """
    500 error handler
    used if there is a server error
    """
    return render_template('500.html'), 500


if __name__ == '__main__':
    analyzer = Analyzer()
    server = SocketIOServer(('', PORT), app, resource="socket.io")
    tw_thread = TweetWeather(server, analyzer, name="Tweet-Weather-Thread")
    tw_thread.daemon = True
    gevent.spawn(tw_thread.new_post, server)
    gevent.spawn(tw_thread.connexion_lost, server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        tw_thread.stop()
        server.stop()
        sys.exit()
