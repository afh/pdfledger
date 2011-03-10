#!/usr/bin/env python
"""
Copyright Gerald Kaszuba 2008

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))

from pygooglechart import PieChart2D
from pygooglechart import PieChart3D

width = 600
height = 400

def month_breakdown():

    #open file
    f = open('month_breakdown.txt')
    #create two lists
    values = []
    labels = []
    #populate lists
    for line in f:
        l, v = line.split('\t')
        values.append(float(v))
        labels.append(l)

    # Create a chart object of 200x100 pixels
    chart = PieChart2D(width, height)

    # Add some data
    chart.add_data(values)

    # Assign the labels to the pie data
    chart.set_pie_labels(labels)

    # Download the chart
    chart.download('monthbreakdown.png')



def hello_world():

    # Create a chart object of 200x100 pixels
    chart = PieChart3D(250, 100)

    # Add some data
    chart.add_data([20, 10])

    # Assign the labels to the pie data
    chart.set_pie_labels(['Hello', 'World'])

    # Download the chart
    chart.download('pie-hello-world.png')

def house_explosions():
    """
    Data from http://indexed.blogspot.com/2007/12/meltdown-indeed.html
    """
    chart = PieChart2D(int(width * 1.7), height)
    chart.add_data([10, 10, 30, 200])
    chart.set_pie_labels([
        'Budding Chemists',
        'Propane issues',
        'Meth Labs',
        'Attempts to escape morgage',
        ])
    chart.download('pie-house-explosions.png')

def main():
#    hello_world()
    month_breakdown()
#    house_explosions()

if __name__ == '__main__':
    main()


