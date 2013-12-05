"""
Module needed by the application to generate the scatter plot
of the sentiment value with the weather value
"""

import os
from pysqlite2 import dbapi2 as db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from cStringIO import StringIO


class ScatterPlot(object):
    """
    This scatter plots includes the data points,
    an ideal correlation line (in green),
    and a fit of the data available (in blue)
    """

    def __init__(self, pol_order=1):
        self.pol_order = pol_order
        self.x = []
        self.y = []

    def load_data(self):
        """
        Gets all data available
        from the database
        """
        if os.path.exists('data.sqlite'):
            cur = db.connect('data.sqlite').cursor()
            cur.execute('SELECT sentimentValue, weatherValue FROM tweets'
                        ' WHERE sentimentValue > 0 ORDER BY id DESC')
            all_fetched = cur.fetchall()
            self.x = [point[0] for point in all_fetched]
            self.y = [point[1] for point in all_fetched]
            return True
        return False

    def set_data(self, x, y):
        """
        Sets x and y from given Lists
        Used for testing purposes
        """
        self.x = list(x)
        self.y = list(y)

    def get_fit_function(self):
        """
        Fits a model following
        the polynomial order given to the class
        """
        mean_x = []
        mean_y = []
        for i in range(0, 8):
            indices = [ind for ind, val in enumerate(self.y) if val == float(i)/7]
            if indices:
                mean_y.append(float(i)/7)
                mean_x.append(np.mean([self.x[j] for j in indices]))
        try:
            fit_fn = np.poly1d(np.polyfit(mean_x, mean_y, self.pol_order))
        except TypeError:  # Empty Lists
            return None
        return fit_fn

    def get_image_data(self):
        """
        Prepares the figure and returns the data
        formatted in a base64 encoded String
        """
        fig = plt.figure()
        axis = fig.add_subplot(1, 1, 1)
        xs = np.linspace(0, 1, 8)
        axis.set_xlim([0, 1])
        axis.set_ylim([0, 1])

        axis.plot(xs, xs,
                  label='Perfect Correlation', color='green')
        fit_fn = self.get_fit_function()
        if (fit_fn):
            axis.plot(xs, fit_fn(xs),
                      label='Observed Correlation', color='blue')
        axis.scatter(self.x, self.y,
                     label='Data Points', color='red')
        plt.xlabel('sentiment')
        plt.ylabel('weather')
        str_io = StringIO()
        fig.savefig(str_io, format='png')
        plt.close("all")
        return str_io.getvalue().encode('base64')
