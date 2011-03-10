#!/usr/bin/env python2.4
# Plot useful charts from a ledger file (just income and expenses right now).
# Requires Pychart, should work on most platforms.
# Home: http://joyful.com/Ledger
# A ledger -p period argument and the pychart arguments may be used. Eg:
#
#   ./ledgerplot.py --help
#   ./ledgerplot.py >incexp.pdf
#   ./ledgerplot.py --format=x11 -p 'from 2007/9/1 to 2007/10/1'
#   ./ledgerplot.py --format=png --scale=2 | display
#
# Tips:
# - pychart 1.39 has a display problem when there is only one data point,
#   grid interval gets set to 10. If this happens set the area's
#   x/y_grid_interval explicitly.

import sys, getopt
from pychart import *
from libledger import *


######################################################################
# process options
#
# pychart does its own processing, try to coexist smoothly
# the below needs to stay current with pychart
# see also pychart/theme.py docstring

def usage(): # string
    print 'Usage: %s [-p "ledgerdateexpr"] [pychartoptions...]' % sys.argv[0] + '\n  '.join([
        '\n',
        '--scale=X: Set the scaling factor to X (default: 1.0).',
        '--format=[ps|png|pdf|x11|svg]: Set the output format (default: ps).',
        '--font-family=NAME: Set the default font family (default: Helvetica).',
        '--font-size=NAME: Set the default font size (default: 9pts).',
        '--line-width=NAME: Set the default line width (default: 0.4).',
        '--debug-level=N: Set the messaging verbosity (default: 0).',
        '--bbox=LEFT,BOTTOM,RIGHT,TOP: Specifies the amount of space (in PS points) to be left in the edges of the picture (default: -1,-1,+1,+1).',
        '--color=[yes|no] (default: yes)',
        ])

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hp:', [
        'help','prefix=','scale=','format=','font-family=','font-size=','line-width=',
        'debug-level=','bbox=',
        'color='
        ])
except getopt.GetoptError:
    usage(); sys.exit(2)
if args:
    usage(); sys.exit(2)

PREFIX = 'ledgerplot'
PERIOD = ''
theme.use_color = 1
for o, v in opts:
    if o in ("-h", "--help"):
        usage(); sys.exit()
    if o == '-p':
        PERIOD = '-p "%s"' % v
        i = sys.argv.index('-p')
        sys.argv[i:i+2] = []
    if o == '--prefix':
        PREFIX = v
        sys.argv = filter(lambda o:not o.startswith('--prefix'),sys.argv)
    # work around pychart 1.39 bug, it doesn't obey --color=no
    if o == '--color':
        if v in ['no','NO','0','']: theme.use_color = 0
        sys.argv = filter(lambda o:not o.startswith('--color'),sys.argv)

theme.get_options()
theme.reinitialize()

######################################################################
# acquire ledger data
# import libledger sets up INCOME, EXPENSES_MONTHLY_ACCOUNT_BALANCES etc.


######################################################################
# draw charts

# We could lay out all the charts ourselves, resizing and positioning them
# in a smart way, returning a combined pdf|ps|png|svg|x11 image.
# We could write one png|svg per chart and let the user lay those out with
# html or whatever.
# For now: we lay out one or more areas, each of which is dumped as a
# png|svg. So eg:
#   ledgerplot --format=png --prefix=mychart; firefox mychart.html (& mychart-*.png)

AREAS = []

# a list of visually distinct colors for plots
# old windows palette
COLORS = [
    color.T(r=0.33203125, g=0.33203125, b=0.99609375), # high blue
    color.T(r=0.99609375, g=0.33203125, b=0.33203125), # high red
    color.T(r=0.33203125, g=0.99609375, b=0.33203125), # high green
    color.T(r=0.33203125, g=0.99609375, b=0.99609375), # high cyan
    color.T(r=0.99609375, g=0.33203125, b=0.99609375), # high magenta
    color.T(r=0.99609375, g=0.99609375, b=0.33203125), # yellow
    color.T(r=0.6640625,  g=0.6640625,  b=0.6640625),  # light gray
    color.T(r=0.0,        g=0.0,        b=0.6640625),  # low blue
    color.T(r=0.6640625,  g=0.0,        b=0.0),        # low red
    color.T(r=0.0,        g=0.6640625,  b=0.0),        # low green
    color.T(r=0.0,        g=0.6640625,  b=0.6640625),  # low cyan
    color.T(r=0.6640625,  g=0.0,        b=0.6640625),  # low magenta
    color.T(r=0.6640625,  g=0.33203125, b=0.0),        # brown
    ]
# same again, darker still
for i in range(len(COLORS)):
    c = COLORS[i]
    COLORS.append(color.T(r=c.r/2,g=c.g/2,b=c.b/2))

# render all areas as a combined image in the default output format
def draw_all(): # () -> None
    global AREAS
    for a in AREAS: a.draw()

# render each area as a png or svg file
def write_all(): # () -> None
    global AREAS
    if theme.output_format not in ['png','svg']: theme.output_format = 'png'
    for i in range(len(AREAS)):
        AREAS[i].draw(canvas.init(image_filename(str(i+1))))

# generate an output image filename
def image_filename(s): # string -> filename
    return '%s%s.%s' % (PREFIX, s, theme.output_format)

# add an area for display, which will hold one or more plots sharing similar coordinates
def add_area(**args): # area_args... -> area
    global AREAS
    AREAS.append(area.T(**args))
    return AREAS[-1]

# add a plot to the most recent area
def add_plot(plotclass, **args): # plot_class plot_args... -> plot
    global AREAS
    p = plotclass(**args)
    AREAS[-1].add_plot(p)
    return p

# various charts

def total_income_bar_graph(): # () -> None
    add_area(
        size=(300,300),
        x_axis = axis.X(label='/14{}total income',
                        format="%d",
                        ),
        x_range = (0,None),
        y_coord = category_coord.T(INCOME,0),
        y_axis = axis.Y(label=None,
#                         format="%s",
                        tic_len=1,
                        tic_label_offset=(-2,3),
                        ),
        x_grid_style=line_style.gray70_dash3,
        y_grid_style=None,
        )
    add_plot(
        bar_plot.T,
        label="Income",
        data=INCOME,
        data_label_format="%.2f",
        data_label_offset=(3,2),
        fill_style=fill_style.green,
        direction="horizontal",
        )

def total_income_pie_graph():
    add_area(
        size=(300,300),
        legend=None,
        x_grid_style=None,
        y_grid_style=None,
        )
    add_plot(
        pie_plot.T,
        data=INCOME,
        arc_offsets=[5]*len(INCOME),
        shadow = (1, -1, fill_style.gray50),
        label_offset = 25,
        arrow_style = arrow.a1,
        )

def monthly_income_line_graph():
    add_area(
        size=(300,300),
        y_axis = axis.Y(label='/14{}income',
                        format="%d",
                        tic_label_offset=(-2,2)
                        ),
        y_range = (0,None),
        x_axis = axis.X(label='/14{}month',
                        format="%d",
                        tic_label_offset=(1,0),
                        ),
        )
    for account, balances in INCOME_ACCOUNT_MONTHLY_BALANCES.items():
        add_plot(
            line_plot.T,
            label=account,
            data=balances,
            data_label_format="%d",
#             data_label_offset=(3,2),
#            tick_mark=tick_mark.plus5,
            )

def total_expenses_bar_graph():
    add_area(
        size=(300,300),
        x_axis = axis.X(label='/14{}total expenses',
                        format="%d",
                        ),
        x_range = (0,None),
        y_coord = category_coord.T(EXPENSES,0),
        y_axis = axis.Y(label=None,
#                         format="%s",
                        tic_len=1,
                        tic_label_offset=(-2,3),
                        ),
        x_grid_style=line_style.gray70_dash3,
        y_grid_style=None,
        )
    add_plot(
        bar_plot.T,
        label="Expenses",
        data=EXPENSES,
        data_label_format="%.2f",
        data_label_offset=(3,2),
        fill_style=fill_style.red,
        direction="horizontal",
        )

def total_expenses_pie_graph():
    add_area(
        size=(300,300),
        legend=None,
        x_grid_style=None,
        y_grid_style=None,
        )
    add_plot(
        pie_plot.T,
        data=EXPENSES,
        arc_offsets=[5]*len(EXPENSES),
        shadow = (1, -1, fill_style.gray50),
        label_offset = 25,
        arrow_style = arrow.a1,
        )

def monthly_expenses_line_graph():
    w, h = 800, 300
    add_area(
        size=(w,h),
        y_axis = axis.Y(label='/14{}expenses',
                        format="%d",
                        tic_label_offset=(-2,2)
                        ),
#        y_range = (0,None),
#        y_grid_interval=1000,
        x_axis = axis.X(label='/14{}month',
                        format="%d",
                        tic_label_offset=(1,0),
                        ),
        x_range=(0,10),
        x_grid_interval=1,
        )
    items = EXPENSES_ACCOUNT_MONTHLY_BALANCES.items()
    items.sort(lambda a,b:cmp(a[0],b[0])) #alphabetise
    items = items[:10]
    for i in range(len(items)):
        account, balances = items[i]
        add_plot(
            line_plot.T,
            label=account,
            data=balances,
            line_style=line_style.T(width=0.8,color=COLORS[i]),
#             data_label_format="%.2f",
#             data_label_offset=(3,2),
            )

def monthly_expenses_bar_graph():
    w, h = 800, 300
    add_area(
        size=(w,h),
        y_axis = axis.Y(label='/14{}expenses',
                        format="%d",
                        tic_label_offset=(-2,2)
                        ),
#        y_range = (0,None),
#        y_grid_interval=1000,
        x_axis = axis.X(label='/14{}month',
                        format="%d",
                        tic_label_offset=(1,0),
                        ),
        x_range=(0,10),
        x_grid_interval=1,
        )
    items = EXPENSES_ACCOUNT_MONTHLY_BALANCES.items()    
    items.sort(lambda a,b:cmp(a[0],b[0])) #alphabetise
    items = items[:10]
    #items.append(('TOTAL',[(m,sum([b for a,b in EXPENSES_MONTHLY_ACCOUNT_BALANCES[m]])) for m in range(1,13)]))
    nmonths = len(items[0][1])
    nitems = len(items)
    for i in range(len(items)):
        account, balances = items[i]
        add_plot(
            bar_plot.T,
            label=account,
            data=balances,
            cluster=(i,len(items)),
            width=0.7*w/nmonths/nitems,
#             line_style=line_style.T(color=COLORS[i]),
            fill_style=fill_style.Plain(bgcolor=COLORS[i]),
#             data_label_format="%.2f",
#             data_label_offset=(3,2),
            )

if INCOME:
    total_income_bar_graph()
    total_income_pie_graph()
    monthly_income_line_graph()

if EXPENSES:
    total_expenses_bar_graph()
    total_expenses_pie_graph()
    monthly_expenses_line_graph()
    monthly_expenses_bar_graph()

#draw_all()
write_all()
