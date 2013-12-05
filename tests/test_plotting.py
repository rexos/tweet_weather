import os
import sys
import pytest
import random
MY_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MY_PATH + '/../server')
from plotting import ScatterPlot


class TestPlotting(object):
    """
    Testing the plotting module
    Since it requires a database,
    this part is not tested and
    fake data is inserted instead
    """

    def test_plotting_empty(self):
        """
        Testing the fit function
        and the image data when no data is available
        or when weather data are random
        and thus not among the allowed discrete values
        """
        plot = ScatterPlot(1)
        img_data = plot.get_image_data()
        assert not(plot.get_fit_function())
        plot.set_data([random.random(), random.random()], [random.random(), random.random()])
        assert not(plot.get_fit_function())
        assert img_data

    def test_plotting(self):
        """
        Testing the fit function
        and the image data when data are available
        """
        plot = ScatterPlot(1)
        plot.set_data([0, 1], [0, 1])
        img_data = plot.get_image_data()
        assert plot.get_fit_function()
        assert img_data
