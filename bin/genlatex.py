#!/usr/bin/env python
from subprocess import Popen,PIPE
import sys
import plot
import pie
import ConfigParser
import getpass

config = ConfigParser.RawConfigParser()
config.read('./examples/pdfledger.cfg')

user = ""
if len(sys.argv) > 1:
    user = sys.argv[1]
else:
    user = getpass.getuser().strip()
    #print "No user provided, using ", user

commands = {}
commands['accts'] = ['--collapse', '--no-total', 'balance']
commands['acctbudget'] = ['-E', '--flat', '--budget', '--no-total', 'balance']
commands['budget'] = ['--flat', '--no-total', 'budget']
commands['retrospective'] = ['--flat', '--no-total', 'balance']
commands['last12months'] = ['-E', '-d', 'd<[today] & d>[today]-365', '--sort', 'd', '--weekly']
commands['next12months'] = ['-E', '--forecast', 'd>[today] & d<[today]+365', '-d', 'd>[today] & d<[today]+365', '--sort', 'd', '--weekly']


LEDGER_FILE = config.get(user, 'ledger_file')
exclude = {}
exclude['acct'] = config.get(user, 'exclude_acct').split(',')
exclude['retrospective'] = config.get(user, 'exclude_retrospective').split(',')
exclude['forecast'] = config.get(user, 'exclude_forecast').split(',')
commands['networth'] = config.get(user, 'networth').split(',')
commands['liquidity'] = config.get(user, 'liquidity').split(',')
commands['cashflow'] = config.get(user, 'cashflow').split(',')
#print "Exclude: ", exclude
#print "Commands: ", commands

def tail(input):
    if(input[-1] == '\n'):
        input = input[:-1]
    input = input.split("\n")
    return str(' '.join(input[-1:])).strip()


def runledger(cmd):
    #print cmd
    ledger = ["ledger", '-f', LEDGER_FILE, '-c']
    output = Popen(ledger + cmd, stdout=PIPE).communicate()[0]
    if(output[-1] == '\n'):
        return output[:-1]
    else:
        return output

def retrospective(acct):
    rtnstring = ""
    subaccts = []
    output = runledger(commands['retrospective'] + ["^"+acct])
    for line in output.split('\n'):
        subaccts += line.split(acct)[-1:]

    #Remove the starting ":" from the subaccount name
    subaccts = [subacct[1:] for subacct in subaccts]

    #Determine which accounts are excluded before iterating
    excluded = [subacct for ex in exclude['retrospective'] for subacct in subaccts if (str(acct + ":" + subacct).find(ex) != -1)]
    subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

    if(len(subaccts) > 0):
        rtnstring += "\section{Retrospectives}"
    for subacct in subaccts:
        fullname = acct + ":" + subacct
        #print retrospective of subaccts with at least 7 transactions when viewed weekly over the last 12 months
        output = runledger(commands['last12months'] + ['-J', 'register'] + ["^" + fullname])
        if(len(output.split('\n')) < 6): continue

        rtnstring += "\subsection{" + subacct + " Retrospective}"

        safename = fullname
        safename = safename.replace(' ', '')
        plot.main("./build/" + safename + "retro", commands['last12months'] + ['-J', 'register'] + ["^" + fullname])
        rtnstring += "\insertplot{" + safename + "retro}"
    return rtnstring

def forecast(acct):
    rtnstring = ""
    #identify budgeted subaccts
    subaccts = []
    output = runledger(commands['acctbudget'] + ["^"+acct])
    for line in output.split('\n'):
        subaccts += line.split(acct)[-1:]
    #Remove the starting ":" from the subaccount name
    subaccts = [subacct[1:] for subacct in subaccts]

    #Determine which accounts are excluded before iterating
    excluded = [subacct for ex in exclude['forecast'] for subacct in subaccts if (str(acct + ":" + subacct).find(ex) != -1)]
    subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

    if(len(subaccts) > 0):
        rtnstring += "\section{Forecasts}"
    for subacct in subaccts:
        fullname = acct + ":" + subacct
        #print forecast of budgeted accts
        rtnstring += "\subsection{" + subacct + " Forecast}"

        safename = fullname
        safename = safename.replace(' ', '')
        plot.main("./build/" + safename + "forecast", commands['next12months'] + ['-J', 'register'] + ["^" + fullname])
        rtnstring += "\insertplot{" + safename + "forecast}"

    return rtnstring


def main():
    latex = ""
    latex += header

    pie.main("./build/", ['-f', LEDGER_FILE, 'balance', 'Expenses'])
    if(config.getboolean(user, 'budget')):
        latex += budget

    output = runledger(commands['accts'])
    accts = []
    for line in output.split('\n'):
        line = line.split()
        accts += line[-1:]

    for acct in accts:
        if(len([ex for ex in exclude['acct'] if (acct.find(ex) != -1)]) > 0): continue
        latex += "\chapter{" + acct + "}"

        latex += retrospective(acct)

        if(config.getboolean(user, 'budget')):
            latex += forecast(acct)

    latex += summary

    latex += r"""\end{document}"""

    f = open("build/pdfledger.tex", 'w')
    f.write(latex)
    f.close()

    #print latex

summary = r"""
\chapter{Summary}

\begin{itemize}

\item The balance of my assets to my liabilities gives my net worth (including retirement funds): """ + tail(runledger(commands['networth'])).replace("Assets", "") + """
\item Removing long term investment and loan accounts gives my net liquidity: """ + tail(runledger(commands['liquidity'])).replace("Assets", "") + """
\item Balancing expenses against income yields your cash flow, or net profit/loss(negative is profit, positive is loss): """ + tail(runledger(commands['cashflow'])) + """

\end{itemize}
"""



header = r"""
\documentclass[pdftex,12pt,letterpaper]{report}
\usepackage[pdftex]{graphicx}
\usepackage[us, 12hr]{datetime}
\usepackage{verbatim}
\usepackage{moreverb}
\usepackage[colorlinks=true]{hyperref}
\let\verbatiminput=\verbatimtabinput %tabs are ignored in verbatim, this corrects for that
\def\verbatimtabsize{4\relax} % set tabs=4 (else my output goes off the screen)
\usepackage{fullpage}

\newcommand{\HRule}{\rule{\linewidth}{0.5mm}}
\newcommand{\insertplot}[1]{\includegraphics[width=0.9\linewidth, keepaspectratio=true]{build/#1}\\[1cm]}

\begin{document}
\input{templates/bettse/title.tex}

\tableofcontents

\chapter*{Introduction}

"I kept account of every farthing I spent, and my expenses were carefully calculated. 
Every little item, such as omnibus fares or postage or a couple of coppers spent on newspapers, would be entered, and the balance struck every evening before going to bed.
That habit has stayed with me ever since, and I know that as a result, though I have had to handle public funds amounting to lakhs, I have succeeded in exercising strict economy in their disbursement, and instead of outstanding debts have had invariably a surplus balance in respect of all the movements I have led.
Let every youth take a leaf out of my book and make it a point to account for everything that comes into and goes out of his pocket, and like me he is sure to be a gainer in the end.
" -- M.K.Gandhi autobiography
"""

budget = r"""
\chapter{Budget}

\begin{figure}
\caption{Breakdown of this months expenses}

\insertplot{monthexpensepie}

\end{figure}

\section{Current month progress}

Negative values indicate to-be-spent funds.  Positive vaues indicate overspending.

\begin{verbatim}
""" + runledger(commands['budget']) + """
\end{verbatim}
"""



if __name__ == "__main__":
    main()

