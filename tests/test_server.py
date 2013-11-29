import os, sys
import server
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../server')


class TestFlaskServer(object):

    def setup(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def test_headers(self):
        rv = self.app.get('/')
        assert rv.data.startswith("<!DOCTYPE html>")

    def test_404(self):
        rv = self.app.get('/random')
        assert rv.status_code == 404

    def test_plot(self):
        rv = self.app.get('/plot?refresh=1&testing=1')
        assert len(rv.data) > 0
