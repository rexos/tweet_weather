"""Perform the data mining tasks through Twitter and OpenWeatherMap's APIs"""

import threading
from pysqlite2 import dbapi2 as db
import simplejson as jsn
import urllib
import tweepy
import os
import time

# secret twitter app credentials
CONSUMER_KEY = "Zlf1laZTxrnydXBMZfeA"
CONSUMER_SECRET = "rNSask1WRb8mLbbzTZo6vAHB27EwNRmy4AA5c3G04"
ACCESS_KEY = "1889545957-BFTycJVNsAgtlfdKbalV1rwTJqoGGhj0iTxIo6k"
ACCESS_SECRET = "NmfEez4FykN1iGZYUfjYzUvUIksNne2xi6Ovo9Wq00"
WEATHER_APPID = "&APPID=4e04cba42b432a01c4226e186f3d23d2"

'''
Dictionary used to map a weather icon to a
weather "score" from 0 (worse) to 8 (best).
Night weathers are never assumed better than
the "Broken Clouds" score of day weathers.
The dictionary is normalized to fit in the
[0,1] range.
TO DO : Snow is being ranked the worst, which is
probably not correct as snow often triggers
positive reactions. Should it be moved ?
'''
WEATHER_DICT = {'13d': 0, '11d': 1, '09d': 2,
                '10d': 3, '50d': 4, '04d': 5,
                '03d': 6, '02d': 7, '01d': 8,
                '13n': 0, '11n': 1, '09n': 2,
                '10n': 3, '50n': 4, '04n': 5,
                '03n': 5, '02n': 5, '01n': 5}
WEATHER_DICT = {k: float(v)/8 for (k, v) in WEATHER_DICT.iteritems()}


class TweetWeather(threading.Thread):
    """
    TweetWeather inherits the Python Thread class.

    Indeed, data mining tasks need to be performed in a separate thread,
    to keep the server running.

    Each new object is stored in the database, and sent to the client
    through a WebSocket.
    """

    def __init__(self, server, analyzer, name=''):
        """
        Checks if there is a working Internet access
        """
        threading.Thread.__init__(self)
        self.name = name
        self.server = server
        self.analyzer = analyzer
        self.root_weather_url = "http://openweathermap.org/data/2.5/weather?lat=%s&lon=%s"
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(auth)  # Initialization of the tweeter API
        self.terminated = False

    def new_post(self, *args):
        """
        Sends the new object in a packet to the client through a WebSocket
        """
        pkt = dict(type="event", name="new_post",
                   args=args, endpoint="/new_posts")
        for _, socket in self.server.sockets.iteritems():
            socket.send_packet(pkt)

    def connexion_lost(self, *args):
        """
        Sends a notification packet to let the client know
        that the internet connexion is lost.
        """
        pkt = dict(type="event", name="connexion_lost",
                   args=args, endpoint="/new_posts")
        for _, socket in self.server.sockets.iteritems():
            socket.send_packet(pkt)

    def run(self):
        init_database()
        self.gather_tweets()
        self.__init__(self.server, self.analyzer, name=self.name)

    def parse_text(self, status):
        """
        preforms a very basic sentiment analysis on
        a single tweet by comparing the most
        significative words found on the afinn
        word-value list. Furthermore gets the
        weather conditions from "http://openweathermap.org"
        of the location where the tweet has been written
        and saves the result in the database.
        """
        conn = db.connect('data.sqlite')
        cursor = conn.cursor()
        score = self.analyzer.analyze(status.text)
        weather_url = self.root_weather_url % tuple(
            [str(x) for x in status.coordinates['coordinates']])
        response = urllib.urlopen(weather_url)
        try:
            weather = jsn.load(response)
        except jsn.JSONDecodeError:
            print('Program --> Tweet not saved due to invalid weather json')
        else:
            if 'weather' in weather.keys():
                main = weather['weather'][0]
                print(main['main'], status.text, score)

                correlation_score = abs(score-WEATHER_DICT[main['icon']])

                cursor.execute("INSERT INTO tweets(sentimentValue,"
                               "weatherValue, correlationScore, weather,"
                               "latitude,longitude,infos)"
                               "VALUES(?, ?, ?, ?, ?, ?, ?)",
                               [score, WEATHER_DICT[main['icon']],
                                correlation_score, main['main'],
                                status.coordinates['coordinates'][1],
                                status.coordinates['coordinates'][0],
                                main['description']])
                self.new_post(score, main['main'], main['description'],
                              status.coordinates['coordinates'][1],
                              status.coordinates['coordinates'][0],
                              correlation_score)
                conn.commit()
        conn.close()

    def gather_tweets(self):
        """
        Performs data mining on tweets which have localization information
        using the Twitter API (and the tweepy wrapper)
        """
        print('Fetching, localizing and analyzing Twitter '
              'stream data ( could take a while due to '
              'the few geotagged tweets ) ...')
        filtered_tweets = []
        query = 'lang:en'
        tweet_pages = tweepy.Cursor(self.api.search,
                                    q=query, lang='en',
                                    count=100, result_type="recent",
                                    include_entities=True).pages()
        while True:
            try:
                tweets = next(tweet_pages)
            except tweepy.error.TweepError as exc:
                if exc.message[0]['code'] == 88:  # Rate Limit Exceeded
                    print "Rate Limit Exceeded. Waiting for 15 minutes."
                    time.sleep(60*15)
                tweets = next(tweet_pages)
            except KeyboardInterrupt:
                self.stop()

            filtered_tweets = [tweet for tweet in tweets if tweet.coordinates]
            if not filtered_tweets:  # No tweet with coordinates on that page
                continue
            for filtered_tweet in filtered_tweets:
                self.parse_text(filtered_tweet)
            if self.terminated:
                break

    def stop(self):
        """
        Stops the thread
        """
        self.terminated = True


def init_database():
    """
    Initializes an sqlite database where evaluated tweets
    will be saved the table created has an id primary key
    attribute, a main value for the weather and a short
    description
    """
    if not os.path.exists('data.sqlite'):
        print("Initializing sqlite database for further analysis ...")
        conn = db.connect('data.sqlite')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE tweets(" +
                       "id integer PRIMARY KEY AUTOINCREMENT," +
                       "sentimentValue real NOT NULL," +
                       "weatherValue real NOT NULL," +
                       "correlationScore real NOT NULL," +
                       "weather VARCHAR(255) NOT NULL," +
                       "latitude REAL NOT NULL," +
                       "longitude REAL NOT NULL," +
                       "infos VARCHAR(255) )")
        conn.commit()
        conn.close()
        print(">> Done <<")
    else:
        print("Connecting to sqlite database")
        print(">> Done <<")
