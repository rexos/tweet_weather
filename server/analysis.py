"""
Module needed by the application to analyze a single tweet
and give it a sentiment score
"""

import numpy as np
import math
import urllib
import os
import re


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
        self.comp_list = {}
        self.afinn_url = "http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip"
        self.url = "https://dl.dropbox.com/u/3773091/Twitter%20Sentiment/Twitter%20sentiment%20analysis.zip"
        urllib.urlretrieve(self.afinn_url, 'word_list.zip')
        word_list_zip = zipfile.ZipFile('word_list.zip')
        self.comp_list = {unicode(k, 'utf-8'): int(v)  # reads AFINN list
                          for (k, v) in [line.split('\t') for line in open(word_list_zip.extract('AFINN/AFINN-111.txt'))]}
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir, 'my_list.txt'), 'r') as comp_file:  # reads larger list
            for line in comp_file:
                data = line.split('\t')
                self.comp_list[data[0]] = int(float(data[1].strip())) - 5

        with open(os.path.join(script_dir, 'emoticons.csv'), 'r') as smiles:  # reads emoticons file
            for line in smiles:
                data = line.split('\t')
                self.comp_list[data[0]] = int(data[1].strip())

        # clean temporary files on the fly
        values = np.array(self.comp_list.values())
        self.mean = np.mean(values)
        self.deviation = math.sqrt(sum([pow(x - self.mean, 2) for x in values])
                                   / float(len(values)))
        os.remove('word_list.zip')
        os.remove('AFINN/AFINN-111.txt')
        os.rmdir('AFINN')

    def analyze(self, tweet):
        """
        Analyzes the body of a tweet by comparing words to the
        AFINN word-value list and using a gaussian distribution
        to compute the weight of each word
        """
        emoticons_groups = re.findall(r"([0-9'\&\-\.\/\(\)=:;]+)|((?::|;|=)(?:-)?(?:\)|D|P))|(<3)", tweet)
        emoticons = [x[0] for x in emoticons_groups if x[0] != '']  # we have three groups in our regexp so we need to check everyone of them
        emoticons.extend([x[1] for x in emoticons_groups if x[1] != ''])
        emoticons.extend([x[2] for x in emoticons_groups if x[2] != ''])
        data = [self.comp_list.get(word, 0) for word in tweet.split(' ')]
        data.extend([self.comp_list.get(e, 0) for e in emoticons])
        ctg_count = {'positive': 0, 'negative': 0, 'neutral': 0}  # dict containing the number of positive negative and neutral words in the current tweet
        ctg_total = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}  # dict containing the sum respectively for positive negative and neutral words
        threshold = 22.5

        # computes categories cardinality and global sum of values of each word in tweet
        vals = self.categories_cardinality(tweet, ctg_count)
        # weights each category
        tot_pos, tot_neg, tot_neu = self.weight_categories(data, ctg_total, ctg_count)
        print( tot_pos, tot_neg, tot_neu )
        if vals:
            total = (sum([tot_pos, tot_neg, tot_neu]) / vals) + threshold
        else:
            total = (sum([tot_pos, tot_neg, tot_neu])) + threshold
        if total > 2*threshold:
            total = 2*threshold
        elif total < 0:
            total = 0
        else:
            pass
        return total / (2*threshold)

    def weight_categories(self, data, ctg_total, ctg_count):
        """
        Computes the weight in terms of word value of each category
        of words ( positive, negative, neutral )
        """
        for value in data:
            if value > 0:
                ctg_total['positive'] = ctg_total['positive'] + (value / espone(value, self.mean, self.deviation))
            elif value < 0:
                ctg_total['negative'] = ctg_total['negative'] + (value / espone(value, self.mean, self.deviation))
            else:
                ctg_total['neutral'] = ctg_total['neutral'] + espone(value, self.mean, self.deviation)
        tot_pos = ctg_total['positive'] * ctg_count['positive']
        tot_neg = ctg_total['negative'] * ctg_count['negative']
        tot_neu = ctg_total['neutral'] * ctg_count['neutral']
        return tot_pos, tot_neg, tot_neu

    def categories_cardinality(self, tweet, ctg_count):
        """
        Computes the cardinality in terms of number of words belonging
        to each category ( positive, negative, neutral ) returns also
        the sum of the absolute values of each word.
        """
        vals = 0
        for word in (tweet.lower()).split(' '):
            temp = self.comp_list.get(word, 100)
            if temp > 0 and temp < 100:
                ctg_count['positive'] = ctg_count.get('positive') + 1
                vals = vals + abs(temp)
            elif temp < 0:
                ctg_count['negative'] = ctg_count.get('negative') + 1
                vals = vals + abs(temp)
            elif temp == 0:
                ctg_count['neutral'] = ctg_count.get('neutral') + 1
                vals = vals + abs(temp)
            else:
                pass
        return vals


def espone(value, mean, deviation):
    """
    The "Likelihood" function using a gaussian probability
    function.
    """
    return math.exp(-(pow((value - mean), 2)) / (2*pow(deviation, 2)))
