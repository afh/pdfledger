#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

"""
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker
from subprocess import Popen,PIPE
import sys
import locale

locale.setlocale(locale.LC_ALL, '' )

def price(x, pos):
    return unicode(locale.currency(x, grouping=True), 'utf-8')
def usage():
    print "Usage: " + sys.argv[0] + " <imagename> <paramters1> <parameter2> ..."

years    = mdates.YearLocator()   # every year
months   = mdates.MonthLocator()  # every month
days     = mdates.DayLocator()    # every day
weeks    = mdates.WeekdayLocator(byweekday=mdates.MO, interval=1)
yearsFmt = mdates.DateFormatter('%Y')
monthsFmt = mdates.DateFormatter('%m/%Y')
daysFmt = mdates.DateFormatter('%m/%d')
#moneyFmt = ticker.FormatStrFormatter(unicode('%s%%1.2f'%currency, 'utf-8'))
moneyFmt = ticker.FuncFormatter(price)

def main(output_file, parameters):
    output = Popen(["ledger"] + parameters, stdout=PIPE).communicate()[0]
    times = []
    values = []
    for line in output.split('\n'):
        if(line == ""):
            continue
        times.append(datetime.datetime.strptime(line.split()[0], "%Y-%m-%d"))
        values.append(float(line.split()[1].replace(',', '.')))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(times, values)

    daterange = (max(times) - min(times)).days
    # format the ticks
    if(daterange < 15 ):
        ax.xaxis.set_major_locator(days)
        ax.xaxis.set_major_formatter(daysFmt)
    if(daterange < 35 ):
        ax.xaxis.set_major_locator(weeks)
        ax.xaxis.set_major_formatter(daysFmt)
    elif(daterange < 90):
        ax.xaxis.set_major_locator(weeks)
        ax.xaxis.set_major_formatter(monthsFmt)
    elif(daterange < 400):
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthsFmt)
    else:
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)

    ax.yaxis.set_major_formatter(moneyFmt)

    daterange = datetime.timedelta(int(round(daterange * .05)))
    datemin = min(times) - daterange
    datemax = max(times) + daterange
    ax.set_xlim(datemin, datemax)

    ax.set_ylim(min(values + [0.0]) * 1.1, max(values + [0.0]) * 1.1)

    # format the coords message box
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.format_ydata = price
    ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
    fig.autofmt_xdate()

    plt.savefig(output_file+".pdf")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2:])
    else:
        usage()
        exit()

