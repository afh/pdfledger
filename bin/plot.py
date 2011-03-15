#!/usr/bin/env python
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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
from subprocess import Popen,PIPE
import sys

def usage():
    print "Usage: " + sys.argv[0] + " <imagename> <paramters1> <parameter2> ..."

years    = mdates.YearLocator()   # every year
months   = mdates.MonthLocator()  # every month
days     = mdates.DayLocator()
yearsFmt = mdates.DateFormatter('%Y')
monthsFmt = mdates.DateFormatter('%m-%d')

if len(sys.argv) > 2:
    output_file = sys.argv[1]
    parameters = sys.argv[2:]
else:
    usage()
    exit()

output = Popen(["ledger"] + parameters, stdout=PIPE).communicate()[0]
times = []
values = []
for line in output.split('\n'):
    if(line == ""):
        continue
    times.append(datetime.datetime.strptime(line.split()[0], "%Y-%m-%d"))
    values.append(float(line.split()[1]))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(times, values)


daterange = datetime.timedelta(int(round((max(times) - min(times)).days * .10)))


# format the ticks
if(daterange.days > 30):
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
else:
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(days)



datemin = min(times) - daterange
datemax = max(times) + daterange
ax.set_xlim(datemin, datemax)

# format the coords message box
def price(x): return '$%1.2f'%x
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = price
ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.savefig(output_file+".png")
