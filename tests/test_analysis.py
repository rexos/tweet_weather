import os
import sys
MY_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MY_PATH + '/../server')
from analysis import Analyzer


class TestAnalysis(object):
    """
    Testing the analysis module
    which deals with sentiment analysis
    """

    def test_espone(self):
        """
        Testing normal distribution
        value for 0 mean and 1 variance
        """
        from analysis import espone
        assert espone(0, 0, 1) == 1.0

    def test_analyze_empty(self):
        """
        Testing empty tweets
        and tweets including words not
        in the dictionary
        """
        ana = Analyzer()
        assert ana.analyze("") == 0.5
        assert ana.analyze("hzoehfsdl") == 0.5

    def test_analyze_bounds(self):
        """
        Testing the bounds of the tweets values
        """
        ana = Analyzer()
        assert ana.analyze("this is a test neutral tweet") <= 1.0
        assert ana.analyze("this is a test neutral tweet") >= 0.0

    def test_analyze_judgement(self):
        """
        Testing the proper judgement of the sentiment analysis:
        * positive and negative
        * best and worse tweet values
        """
        ana = Analyzer()
        assert ana.analyze(":)") > 0.5 and ana.analyze(":'(") < 0.5
        assert ana.analyze("yahoo yahoo yahoo") == 1.0
        assert ana.analyze("zzz zzz zzz zzz zzz") == 0.0

    def test_analyze_judgement_weight(self):
        """
        Testing the value order
        of arbitrary tweets
        """
        ana = Analyzer()
        assert ana.analyze("i am so happy, great day :D") > ana.analyze("i am so happy :D")
        assert ana.analyze("so sad, feeling depressed :'(") < ana.analyze("so depressed :'(")

    def test_categories_cardinality(self):
        """
        Testing the cardinality of the different
        categorie sums (positive, negative, neutral)
        """
        ana = Analyzer()
        ctg_count = {'positive': 0, 'negative': 0, 'neutral': 0}
        text = 'great day today lol ;) but still have to work'
        assert ana.categories_cardinality(text, ctg_count) == 15
        assert ctg_count['positive'] == 4  # great day lol ;)
        assert ctg_count['neutral'] == 1  # today
        assert ctg_count['negative'] == 2  # work still

    def test_categories_weight(self):
        """
        Testing the weights of the different
        categorie sums (positive, negative, neutral)
        """
        ana = Analyzer()
        ctg_total = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        ctg_count = {'positive': 4, 'negative': 2, 'neutral': 1}
        data = [2, 3, 0, 2, 2, 0, -4, 0, 0, -2, 2]
        tot_pos, tot_neg, tot_neu = ana.weight_categories(data, ctg_total, ctg_count)
        assert (tot_pos, tot_neg, tot_neu) == (99.47646509317096, -49.392885301738836, 3.9750077625545726)
