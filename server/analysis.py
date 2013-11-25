"""
Module needed by the application to analyze a single tweet
and give it a sentiment score
"""

import numpy as np
import math
import urllib
import os
import nltk


class Analyzer(object):
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
        # set of tags needed for the bag of words extraction
        self.tags = ['JJ', 'NN', 'VB', 'NNS', 'JJR', 'JJS', 'PRP', 'RBR', 'RBS']
        self.comp_list = {}
        self.afinn_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"
        self.url = "https://dl.dropbox.com/u/3773091/Twitter%20Sentiment/Twitter%20sentiment%20analysis.zip"
        urllib.urlretrieve(self.afinn_url, 'word_list.zip')
        word_list_zip = zipfile.ZipFile('word_list.zip')
        self.comp_list = {unicode(k, 'utf-8'): int(v)+5
                          for (k, v) in [line.split('\t') for line in open(word_list_zip.extract('AFINN/AFINN-111.txt'))]}
        with open('my_list.txt', 'r') as comp_file:
            for line in comp_file:
                data = line.split('\t')
                self.comp_list[data[0]] = int(float(data[1].strip()))
        print(len(self.comp_list))
        # clean temporary files on the fly
        os.remove('word_list.zip')
        os.remove('AFINN/AFINN-111.txt')
        os.rmdir('AFINN')

    def analyze(self, tweet):
        """
        Analyzes the body of a tweet by comparing words to the
        AFINN word-value list and using a gaussian distribution
        to compute the weight of each word
        """
        values = np.array(self.comp_list.values())
        data = self.parse(tweet)
        data = [int(x) for x in data if x != 0]
        mean_data = np.mean(data)
        mean = np.mean(values)
        deviation = math.sqrt(sum([pow(x - mean, 2) for x in values])
                              / float(len(values)))
        total = 0

        for value in data:
            total = total + (value * espone(value, mean, deviation))

        if sum(data):
            total = total / float(sum(data))

        if mean_data > mean:
            return 1 - total
        else:
            return total

    def parse(self, tweet):
        """
        Extracts the most meaningful words (bag of words) from the
        tweets body text and returns a list composed
        by them. Uses the nltk module to achieve this.
        """
        tokens = nltk.word_tokenize(tweet)
        tagged = nltk.pos_tag(tokens)
        parsed = [word for (word, tag) in tagged if tag in self.tags]
        return parsed


def espone(value, mean, deviation):
    """
    The "Likelihood" function using a gaussian probability
    function.
    """
    return math.exp(-(pow((value - mean), 2)) / (2*pow(deviation, 2)))
