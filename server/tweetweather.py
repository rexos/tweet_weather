import threading
from pysqlite2 import dbapi2 as db
import simplejson as jsn
import urllib
import tweepy
import os

# secret twitter app credentials
consumer_key = "Zlf1laZTxrnydXBMZfeA"
consumer_secret = "rNSask1WRb8mLbbzTZo6vAHB27EwNRmy4AA5c3G04"
access_key = "1889545957-BFTycJVNsAgtlfdKbalV1rwTJqoGGhj0iTxIo6k"
access_secret = "NmfEez4FykN1iGZYUfjYzUvUIksNne2xi6Ovo9Wq00"
weather_appid = "&APPID=4e04cba42b432a01c4226e186f3d23d2"

class TweetWeather(threading.Thread):

	def __init__(self, server, analyzer, name = ''):
		import sys
		"""
		Checks if there is a working Internet access
		"""
		try:
			res = urllib.urlopen( 'http://google.com' )
		except:
			sys.exit( "Absent Internet Access, please retry" )
		threading.Thread.__init__(self)
		self.name = name
		self.server = server
		self.analyzer = analyzer
		self.root_weather_url = "http://openweathermap.org/data/2.5/weather?lat=%s&lon=%s"
		self.Terminated = False

	def new_post(self, *args):
		pkt = dict(type="event", name="new_post", args=args, endpoint="/new_posts")
		for sessid, socket in self.server.sockets.iteritems():
			socket.send_packet(pkt)

	def run(self):
		self.init_twitter_api()
		self.init_database()
		self.gatherTweets()
		self.__init__(self.server,self.analyzer, name=self.name)

	def init_twitter_api(self):
		# obtaining twitter app authorization
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_key, access_secret)
		self.gathered = []
		self.api = tweepy.API(auth)

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
					                   "latitude REAL NOT NULL," + \
					                   "longitude REAL NOT NULL," + \
							   "infos VARCHAR(255) )")
			conn.commit()
			conn.close()
			print(">> Done <<")
		else:
			print("Connecting to sqlite database")
			print(">> Done <<")

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
		score = self.analyzer.analyze(status.text)
		weather_url = self.root_weather_url %tuple( map( lambda x: str(x), status.coordinates['coordinates'] ) )
		response = urllib.urlopen(weather_url)
		try:
			weather = jsn.load( response )
		except:
			print('Program --> Tweet not saved due to invalid weather json')
		else:
			if 'weather' in weather.keys():
				main = weather['weather'][0]
				print( main['main'], status.text, score )
				
				self.gathered.append( tuple((score, status.coordinates['coordinates'], main['main'])) )
				cursor.execute("INSERT INTO tweets(value,weather,latitude,longitude,infos) VALUES(?, ?, ?, ?, ?)", 
					       [score, main['main'], status.coordinates['coordinates'][0], status.coordinates['coordinates'][1], main['description']])
				self.new_post(score, main['main'], main['description'])
				conn.commit()
		conn.close()

	def gatherTweets(self):
		print( 'Fetching, localizing and analyzing Twitter stream data ( could take a while due to the few geotagged tweets ) ...' )

		query = 'lang:en'
		page_count = 0
		for tweets in tweepy.Cursor(self.api.search, q=query, lang='en', count=100, result_type="recent", include_entities=True).pages():
			filteredTweets = [tweet for tweet in tweets if tweet.coordinates]
			if  not filteredTweets:
				continue
			page_count += 1
			for filteredTweet in filteredTweets:
				self.parse_text(filteredTweet)

			if page_count >= 200 or self.Terminated:
				break

	def stop(self):
		self.Terminated = True
