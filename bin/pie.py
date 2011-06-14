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

def sanatize(money):
    return money.replace('$','').replace(',','').strip()


def main(output_loc, parameters):
    parameters += ['-p', 'this month','--flat', '--no-total', '-F', '%(account)\t%(amount)\n']
    command = ["ledger"] + parameters
    #print ' '.join(command)
    output = Popen(command, stdout=PIPE).communicate()[0]
    labels = []
    values = []
    for line in output.split('\n'):
        if(line == ""):
            continue
        fields = line.split('\t')
        label = fields[0]
        values.append(float(sanatize(fields[1])))
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

