#!/usr/bin/env python
"""
Make a pie chart - see
http://matplotlib.sf.net/matplotlib.pylab.html#-pie for the docstring.

This example shows a basic pie chart with labels optional features,
like autolabeling the percentage, offsetting a slice with "explode"
and adding a shadow.

Requires matplotlib0-0.70 or later

"""
from pylab import *
from subprocess import Popen,PIPE
import sys


output_loc = "./"
if len(sys.argv) > 1:
    output_loc = sys.argv[1]
if len(sys.argv) > 2:
    parameters = sys.argv[2:]

parameters += ['-p', 'this month','--flat', '--no-total', 'balance', 'Expenses']
output = Popen(["ledger"] + parameters, stdout=PIPE).communicate()[0]
labels = []
values = []
for line in output.split('\n'):
    if(line == ""):
        continue
    values.append(float(line.split()[0]))
    labels.append(line.split()[2])

# make a square figure and axes
figure(1, figsize=(8,8))
ax = axes([0.1, 0.1, 0.8, 0.8])

pie(values, explode=None, labels=labels, autopct='%1.1f%%', shadow=False)
title('Breakdown of this months expenses', bbox={'facecolor':'0.8', 'pad':5})

savefig(output_loc+"monthexpensepie.png")
