#!/usr/bin/env python

from subprocess import Popen,PIPE
import sys

# do this before importing pylab or pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker

from pylab import *

import datetime
import numpy as np

import locale
locale.setlocale(locale.LC_ALL, '' )

def price(x, pos):
    return unicode(locale.currency(x, grouping=True), 'utf-8')


def main(output_loc, parameters):
    moneyFmt = ticker.FuncFormatter(price)
    data_parameters = ['-F', '%(amount)\n', '-E', '--budget', '-p', 'this year', '-d', 'd < [this month]', '-M', 'reg'] + parameters
    parameters += ['-F', '%(account)\n', '-p', 'this month', '--flat', '--no-total', '--budget', '-M', 'bal', '^exp']

    output = Popen(["ledger"] + parameters, stdout=PIPE).communicate()[0]
    accounts = [acct for acct in output.split('\n') if acct != ""]

    data = []
    labels = []
    for acct in accounts:
        output = Popen(["ledger"] + data_parameters + ["^" + acct], stdout=PIPE).communicate()[0]
        values = []
        for value in output.split('\n'):
            if value == "":
                continue
            value = value.replace('$', '')
            value = float(value.strip())
            values.append(value)
        data.append(values)
        labels.append(acct.split(':')[-1])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    boxplot(data)

    title('Boxplot of expenses by month this year')
    ax.yaxis.set_major_formatter(moneyFmt)
    ax.format_ydata = price

    fig.autofmt_xdate()
    ax.set_xticklabels(labels)

    savefig(output_loc+"budget_boxplot.pdf")



if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2:])
    elif len(sys.argv) > 1:
        main("./", sys.argv[2:])
    else:
        exit()

