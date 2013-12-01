import os, sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../server')

class TestAnalysis(object):

    def test_espone(self):
        from analysis import espone
        assert espone(0,0,1) == 1.0

    def test_parse(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.parse("going to the mall now") == ['mall']

    def test_parse_empty(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.parse("going now") == []

    def test_analyze_empty(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.analyze("") == 0.5

    def test_analyze_bounds(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.analyze("this is a test neutral tweet") <= 1.0 and ana.analyze("this is a test neutral tweet") >= 0.0

    def test_analyze_judgement(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.analyze(":)") > 0.5 and ana.analyze(":'(") < 0.5
        assert ana.analyze("yahoo yahoo yahoo") == 1.0
        assert ana.analyze("zzz zzz zzz zzz zzz") == 0.0

    def test_analyze_judgement_more(self):
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.analyze("i am so happy, great day :D") > ana.analyze("i am so happy :D") and ana.analyze("so sad, feeling depressed :'(") < ana.analyze("so depressed :'(")
