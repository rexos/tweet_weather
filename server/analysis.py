"""
Module needed by the application to analyze a single tweet
and give it a sentiment score
"""

import numpy as np
import math
import urllib
import os
import nltk

class Parser():
    """
    The Parser class is used to parse the body of a tweet
    extract the most meaningful words from it and return
    a list of them
    """
    def __init__(self):
        """
        Parser constructor which initializes a set of tags
        needed for the bag of words extraction
        """
        self.tags = ['JJ', 'NN', 'VB', 'NNS', 'JJR', 'JJS', 'PRP', 'RBR', 'RBS']

    def parse(self, text):
        """
        Extracts the most meaningful words (bag of words) from the
        tweets body text and returns a list composed
        by them. Uses the nltk module to achieve this.
        """
        tokens = nltk.word_tokenize( text )
        tagged = nltk.pos_tag(tokens)
        parsed = [ word for (word, tag) in tagged if tag in self.tags ]
        return parsed

class Analyzer():
    """
    Analyzer is used to give a real value to the sentiment found
    in a tweet text.
    """
    def __init__(self):
        """
        Analyzer constructor, urls and external data
        management hard coded.
        """
        import zipfile
        self.list = {}
        self.parser = Parser()
        self.afinn_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"
        self.url = "https://dl.dropbox.com/u/3773091/Twitter%20Sentiment/Twitter%20sentiment%20analysis.zip"
        urllib.urlretrieve( self.afinn_url, 'word_list.zip' )
        zip = zipfile.ZipFile('word_list.zip')
        self.list = dict(map(lambda (k, v): ( unicode(k, 'utf-8'), int(v)+5 ),
                 [ line.split('\t') for line in open(zip.extract('AFINN/AFINN-111.txt')) ]))

        # clean temporary files on the fly
        os.remove('word_list.zip')
        os.remove('AFINN/AFINN-111.txt')
        os.rmdir('AFINN')

    def espone( self, x, mean, deviation ):
        """
        The "Likelihood" function using a gaussian probability
        function.
        """
        return math.exp( -( pow( (x - mean ), 2 )) / (2*pow( deviation, 2 )) )

    def analyze(self, tweet):
        """
        Analyzes the body of a tweet by comparing words to the
        AFINN word-value list and using a gaussian distribution
        to compute the weight of each word
        """
        values = np.array(self.list.values())
        data = [ self.list.get( word, 0 ) for word in tweet.split(" ") ]
        data = [ int(x) for x in data if x != 0 ]
        mean_data = np.mean( data )
        mean = np.mean( values )
        deviation = math.sqrt( sum( [ pow(x - mean, 2) for x in values ] )
                               / float( len(values) ))
        total = 0

        for d in data:
            total = total+( d * self.espone(d, mean, deviation) )

        if sum(data):
            total = total / float(sum(data))

        if mean_data > mean:
            return 1 - total
        else:
            return total
