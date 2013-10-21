__version__ = 0.01
__author__ = "Alex Pellegrini"
__all__ = ["WeatherTwitterStream"]

"""
PYTHON script which attempts to attach to the Twitter stream
downloading live tweets and perform a raw sentiment analysis 
on which of them has a geo-location.
After that connects to opensweathermap.org to get real-time
weather conditions of the place the tweet come from and plots 
a barchart as a result to display any basic relationship between
the weather and people's mood.
The program is supposed to be slow due to the fact that the 
localizable tweets are very few. 
"""

import sys
import tweepy
from numpy import arange
import nltk
import urllib
import zipfile
import os
import matplotlib.pyplot as plt
import simplejson as jsn
from pysqlite2 import dbapi2 as db # sqlite db module


# secret twitter app credentials
consumer_key = "Zlf1laZTxrnydXBMZfeA"
consumer_secret = "rNSask1WRb8mLbbzTZo6vAHB27EwNRmy4AA5c3G04"
access_key = "1889545957-V1RGrOLo5W4gQPycPB8cHErV1kr5DMlbaGihCe4"
access_secret = "VKDlwwsCM8VtjsD8XvkFGwMmL4uxDbV32wQu8jKdoAo" 
weather_appid = "&APPID=4e04cba42b432a01c4226e186f3d23d2"

# obtaining twitter app authorization
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
gathered = []
root_weather_url = "http://openweathermap.org/data/2.5/weather?lat=%s&lon=%s"
afinn_list_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"

"""
Checks if there is a working Internet access
"""
try:
    res = urllib.urlopen( 'http://google.com' )
except:
    sys.exit( "Absent Internet Access, please retry" )

print('Downloading, unzipping and importing external data ...')
urllib.urlretrieve( afinn_list_url, 'afinn.zip' )
zip = zipfile.ZipFile('afinn.zip')
afinn = dict(map(lambda (k,v): ( unicode(k, 'utf-8'), int(v) ), 
                 [ line.split('\t') for line in open(zip.extract('AFINN/AFINN-111.txt')) ]))
print('>> Done <<')

try:
    number = int( raw_input('Number of tweets to analyze --> ') )
except ValueError:
    print( 'Wrong input, retry' )
    sys.exit(1)

def init_database():
    """
    Initializes an sqlite database where evaluated tweets 
    will be saved the table created has an id primary key
    attribute, a main value for the weather and a short
    description
    """
    if not os.path.exists('data.sqlite'):
        print("Initializing sqlite database for further analysis ...")
        conn = db.connect( 'data.sqlite' )
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE tweets(" + \
                           "id integer PRIMARY KEY AUTOINCREMENT," + \
                           "value integer NOT NULL," + \
                           "weather VARCHAR(255) NOT NULL," + \
                           "infos VARCHAR(255) )")
        conn.commit()
        conn.close()
        print(">> Done <<")
    else:
        print("Connecting to sqlite database")
        print(">> Done <<")

def sanitize_text( text ):
    """
    Extracts the most meaningful words from the 
    tweets body text and returns a list composed
    by them.
    """
    tokens = nltk.word_tokenize( text )
    tagged = nltk.pos_tag(tokens)
    parsed = [ word for (word, tag) in tagged if tag in ['JJ', 'NN', 'VB', 'NNS', 'JJR', 'JJS', 'PRP', 'RBR', 'RBS'] ]
    return parsed

def parse_text( status ):
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
    parsed = sanitize_text( status.text )
    score = 0
    for word in parsed:
            score += afinn.get(word,0)
    if score != 0 : 
        weather_url = root_weather_url %tuple( map( lambda x: str(x), status.coordinates['coordinates'] ) )
        response = urllib.urlopen(weather_url)
        try:
            weather = jsn.load( response )
        except:
            print('Program --> Tweet not saved due to invalid weather json')
        else:
            if 'weather' in weather.keys():
                main = weather['weather'][0]
                print( main['main'], status.text )
                gathered.append( tuple((score, status.coordinates['coordinates'], main['main'])) )
                cursor.execute("INSERT INTO tweets(value,weather,infos) VALUES(?, ?, ?)", [score, main['main'], main['description']])
                conn.commit()
    conn.close()

def plot_data():
    """
    plot_data() plots a barchart showing average 
    values gathered from (raw) analized tweets in
    the database
    """
    conn = db.connect('data.sqlite')
    cur = conn.cursor()
    tweets = cur.execute('SELECT weather, COUNT(*), AVG(value) FROM tweets GROUP BY weather').fetchall()
    data = {}
    for x in tweets:
        data[x[0]] = (x[1],x[2])
    plt.bar( arange(len(data)), map( lambda x : x[1], data.values() ), 1 )
    plt.xticks( map(lambda x: x+0.5,arange(len( data ))), data.keys() )
    plt.suptitle('Raw Extimation about how weather affects the people\'s mood \n bar heigths (starting from 0) corressponds to good mood (> 0) bad mood (< 0)')
    plt.xlabel('Main Weather Conditions')
    plt.ylabel('Mood')
    plt.show()
    conn.close()

def clean_tmp_files():
    print("Cleaning current directory from temporary files ...")
    os.remove('afinn.zip')
    os.remove('AFINN/AFINN-111.txt')
    os.rmdir('AFINN')
    print(">> Done <<")

class Listener(tweepy.StreamListener):
    """
    Listener class objects are used by the Twitter stream
    object to work on the tweets objects. Customizable.
    """
    def on_status(self, status):
        if status.coordinates :
            parse_text( status )
        if len( gathered ) < number:
            return True
        else:
            print( gathered )
            return False
    def on_error(self, status_code):
        print(sys.stderr, 'Encountered error with status code:', status_code)
        return True

    def on_timeout(self):
        print(sys.stderr, 'Timeout...')
        return True

def main():
    init_database()
    l = Listener()
    streamer = tweepy.Stream( auth=auth, listener=l )
    # get about 1% of incoming tweets
    print( 'Fetching, localizing and analyzing Twitter stream data ( could take a while due to the few geotagged tweets ) ...' )
    streamer.sample()
    plot_data()
    clean_tmp_files()

if __name__ == "__main__":
    main()
