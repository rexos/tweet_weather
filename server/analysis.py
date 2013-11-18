import numpy as np
import scipy.stats
import math
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
        self.list = dict(map(lambda (k,v): ( unicode(k, 'utf-8'), int(v)+5 ), 
                 [ line.split('\t') for line in open(zip.extract('AFINN/AFINN-111.txt')) ]))
        
        # clean temporary files on the fly
        os.remove('word_list.zip')
        os.remove('AFINN/AFINN-111.txt')
        os.rmdir('AFINN')

    def espone( self, x, mean, deviation ):
        return math.exp( -( pow( (x - mean ), 2 )) / (2*pow( deviation, 2 )) )

    def analyze(self, tweet):
        values = np.array(self.list.values())
        data = [ self.list.get( word, 0 ) for word in tweet.split(" ") ]
        data = [ int(x) for x in data if x != 0 ]
        mean_data = np.mean( data )
        mean = np.mean( values )
        deviation = math.sqrt( sum( [ pow(x - mean, 2) for x in values ] ) / float( len(values) ))
        total = 0
        
        for d in data:
            total = total+( d * self.espone(d,mean,deviation) )
        
        if sum(data):
            total = total / float(sum(data))
        
        if mean_data > mean:
            return 1 - total
        else:
            return total
