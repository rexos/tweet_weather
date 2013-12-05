import os
import sys
MY_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MY_PATH + '/../server')
import server


class TestFlaskServer(object):
    """
    Testing a part of the Flask webserver
    """

    def setup(self):
        """
        Called at the beginning of the test module
        Configures the Flask Test Client
        """
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def test_http_routes(self):
        """
        Tests that all routes deliver the
        pages without errors
        """
        response = self.app.get('/')
        assert response.status_code == 200
        response = self.app.get('/list_data')
        assert response.status_code == 200
        response = self.app.get('/map')
        assert response.status_code == 200
        response = self.app.get('/plot')
        assert response.status_code == 200

    def test_error_handlers(self):
        """
        Testing a random URL to
        catch a 404 HTTP errors
        """
        response = self.app.get('/randomurl')
        assert response.status_code == 404

    def test_plot(self):
        """
        Testing the reception of the image
        data when an ajax request is sent
        """
        response = self.app.get('/plot?refresh=1')
        assert len(response.data) > 0
