import os, sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../server')

class TestAnalysis:
    def test_espone(self):
        from analysis import espone
        assert espone(0,0,1) == 1.0

    def test_parse(self,tmpdir):
    	print tmpdir
        from analysis import Analyzer
        ana = Analyzer()
        assert ana.parse("going to the mall now") == ['mall']
        assert ana.parse("going now") == []

