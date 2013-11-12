import numpy as np
import urllib
import os
import nltk


class Parser():
    def __init__(self):
        self.tags = ['JJ', 'NN', 'VB', 'NNS', 'JJR', 'JJS', 'PRP', 'RBR', 'RBS']

    def parse(self, text):
        """
        Extracts the most meaningful words from the
        tweets body text and returns a list composed
        by them.
        """
        tokens = nltk.word_tokenize( text )
        tagged = nltk.pos_tag(tokens)
        parsed = [ word for (word, tag) in tagged if tag in self.tags ]
        return parsed

class Analyzer():

    def __init__(self):
        import zipfile
        self.H = {}
        self.S = {}
        self.parser = Parser()
        self.url = "https://dl.dropbox.com/u/3773091/Twitter%20Sentiment/Twitter%20sentiment%20analysis.zip"
        urllib.urlretrieve( self.url, 'word_list.zip' )
        zip = zipfile.ZipFile('word_list.zip')
        list = zip.extract('twitter_sentiment_list.csv')
        with open(list, 'r') as file:
            file.readline()
            for line in file:
                data = line[:-1].split(',')
                self.H[data[0]] = float(data[1])
                self.S[data[0]] = float(data[2])
        # clean temporary files on the fly
        os.remove('word_list.zip')
        os.remove('twitter_sentiment_list.csv')

    def analyze(self, tweet):
    #evaluates the log probability of tweet happiness ( sadness = 1 - happiness )
        tweet = self.parser.parse(tweet)
        tw_happy = [self.H.get(word,0) for word in tweet]
        tw_sad = [self.S.get(word,0) for word in tweet]
        happy_prob = np.reciprocal( np.exp( np.sum(tw_sad) - np.sum(tw_happy) ) + 1 )
        return happy_prob

