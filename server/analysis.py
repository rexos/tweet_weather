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
        self.list = {}
        self.parser = Parser()
        self.afinn_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"
        self.url = "https://dl.dropbox.com/u/3773091/Twitter%20Sentiment/Twitter%20sentiment%20analysis.zip"
        urllib.urlretrieve( self.afinn_url, 'word_list.zip' )
        zip = zipfile.ZipFile('word_list.zip')
        self.list = dict(map(lambda (k,v): ( unicode(k, 'utf-8'), int(v) ), 
                 [ line.split('\t') for line in open(zip.extract('AFINN/AFINN-111.txt')) ]))
        
        # clean temporary files on the fly
        os.remove('word_list.zip')
        os.remove('AFINN/AFINN-111.txt')
        os.rmdir('AFINN')

    def analyze(self, tweet):
    #evaluates the log probability of tweet happiness ( sadness = 1 - happiness )
        tweet = self.parser.parse(tweet)
        tw_values = [self.list.get(word,0) for word in tweet]
        values = [ int(x) for x in tw_values if x != 0 ]
        print( values )
        length = ( len(values) if len(values) else 1 )
        mean = ( sum( tw_values ) ) / float( length )
        weigth = ( mean + 5 ) / 10.
        return weigth

