from flask import Flask
from flask import render_template
from pysqlite2 import dbapi2 as db
import threading
import sys
import tweepy
from numpy import arange
import nltk
import urllib
import zipfile
import os
import time
import matplotlib.pyplot as plt
import simplejson as jsn
from pysqlite2 import dbapi2 as db # sqlite db module


# secret twitter app credentials
consumer_key = "Zlf1laZTxrnydXBMZfeA"
consumer_secret = "rNSask1WRb8mLbbzTZo6vAHB27EwNRmy4AA5c3G04"
access_key = "1889545957-BFTycJVNsAgtlfdKbalV1rwTJqoGGhj0iTxIo6k"
access_secret = "NmfEez4FykN1iGZYUfjYzUvUIksNne2xi6Ovo9Wq00"
weather_appid = "&APPID=4e04cba42b432a01c4226e186f3d23d2"

# obtaining twitter app authorization
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
gathered = []
root_weather_url = "http://openweathermap.org/data/2.5/weather?lat=%s&lon=%s"
afinn_list_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"
api = tweepy.API(auth)

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

class TweetWeather(threading.Thread):
	def __init__(self, name = ''):
		threading.Thread.__init__(self)
		self.name = name
		self.Terminated = False

	def run(self):
		self.init_database()
		self.gatherTweets()

	def init_database(self):
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

	def sanitize_text(self,text ):
		"""
		Extracts the most meaningful words from the
		tweets body text and returns a list composed
		by them.
		"""
		tokens = nltk.word_tokenize( text )
		tagged = nltk.pos_tag(tokens)
		parsed = [ word for (word, tag) in tagged if tag in ['JJ', 'NN', 'VB', 'NNS', 'JJR', 'JJS', 'PRP', 'RBR', 'RBS'] ]
		return parsed

	def parse_text(self,status ):
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
		parsed = self.sanitize_text( status.text )
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
					print( main['main'], status.text, score )

					gathered.append( tuple((score, status.coordinates['coordinates'], main['main'])) )
					cursor.execute("INSERT INTO tweets(value,weather,infos) VALUES(?, ?, ?)", [score, main['main'], main['description']])
					conn.commit()
		conn.close()

	def clean_tmp_files(self):
		print("Cleaning current directory from temporary files ...")
		os.remove('afinn.zip')
		os.remove('AFINN/AFINN-111.txt')
		os.rmdir('AFINN')
		print(">> Done <<")

	def gatherTweets(self):
		print( 'Fetching, localizing and analyzing Twitter stream data ( could take a while due to the few geotagged tweets ) ...' )

		query = 'lang:en'
		page_count = 0
		for tweets in tweepy.Cursor(api.search, q=query, lang='en', count=100, result_type="recent", include_entities=True).pages():
			filteredTweets = [tweet for tweet in tweets if tweet.coordinates]
			if  not filteredTweets:
				continue
			page_count += 1
			for filteredTweet in filteredTweets:
				self.parse_text(filteredTweet)

			if page_count >= 200 or self.Terminated:
				break

	def stop(self):
		self.clean_tmp_files()
		self.Terminated = True

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
