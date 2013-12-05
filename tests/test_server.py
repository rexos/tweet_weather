import os, sys
import server
import pytest
from pysqlite2 import dbapi2 as db
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../server')

class TestFlaskServer(object):

    def setup(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def test_http_routes(self):
        rv = self.app.get('/')
        assert rv.status_code == 200
        rv = self.app.get('/list_data')
        assert rv.status_code == 200
        rv = self.app.get('/map')
        assert rv.status_code == 200
        rv = self.app.get('/plot')
        assert rv.status_code

    def test_error_handlers(self):
        rv = self.app.get('/randomurl')
        assert rv.status_code == 404
        rv = self.app.get('/plot?refresh=1')
        assert rv.status_code == 500

    def test_plot(self):
        rv = self.app.get('/plot?refresh=1&testing=1')
        assert len(rv.data) > 0
