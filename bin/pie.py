#!/usr/bin/env python
"""
Make a pie chart - see
http://matplotlib.sf.net/matplotlib.pylab.html#-pie for the docstring.

This example shows a basic pie chart with labels optional features,
like autolabeling the percentage, offsetting a slice with "explode"
and adding a shadow.

Requires matplotlib0-0.70 or later

"""
import matplotlib
matplotlib.use('Agg')
from pylab import *
from subprocess import Popen,PIPE
import sys


def main(output_loc, parameters):
    parameters += ['-p', 'this month','--flat', '--no-total']
    output = Popen(["ledger"] + parameters, stdout=PIPE).communicate()[0]
    labels = []
    values = []
    for line in output.split('\n'):
        if(line == ""):
            continue
        values.append(float(line.split()[0]))
        label = line.split()[2]
        labels.append(label.split(':')[-1])

    # make a square figure and axes
    figure(figsize=(8,8), frameon=False)

    ax = axes([0.1, 0.1, 0.8, 0.8])

    pie(values, explode=None, labels=labels, autopct='%1.1f%%', shadow=False)

    savefig(output_loc+"monthexpensepie.pdf")



if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2:])
    elif len(sys.argv) > 1:
        main("./", sys.argv[2:])
    else:
        exit()

