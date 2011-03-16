#!/usr/bin/env python
from subprocess import Popen,PIPE
import sys
import plot
import pie

LEDGER_FILE="/Users/bettse/Dropbox/Finances/201103.lgr"
if len(sys.argv) > 1:
    LEDGER_FILE = sys.argv[1]

ledger = ["ledger", '-f', LEDGER_FILE, '-c']

commands = {}
commands['accts'] = ['--collapse', '--no-total', 'balance']
commands['acctbudget'] = ['--flat', '--budget', '--no-total', 'balance']
commands['budget'] = ['--flat', '--no-total', 'budget']
commands['retrospective'] = ['--flat', '--no-total', 'balance']
commands['last12months'] = ['-d', '"d<[today] & d>[today]-365"', '--sort', 'd', '--weekly']
commands['next12months'] = ['-d', '"d>[today] & d<[today]+365"', '--sort', 'd', '--weekly']
commands['networth'] = ['--collapse', 'bal', '^Assets', '^Liabilities']
commands['liquidity'] = ['--collapse', 'bal', '^Assets', '^Liabilities', 'and not roth']
commands['cashflow'] = ['--collapse', 'bal', '^Expenses', '^Income']

#To be moved to a config later
exclude = {}
exclude['acct'] = ['Equity']
exclude['retrospective'] = ['Expenses', 'Cash']
exclude['forecast'] = ['Equity', 'Salary']

def runledger(cmd):
    return Popen(ledger + cmd, stdout=PIPE).communicate()[0]


def main():

    print header

    pie.main("../build/", ['-f', LEDGER_FILE, 'balance', 'Expenses'])
    print budget

    output = runledger(commands['accts'])
    accts = []
    for line in output.split('\n'):
        if(line == ""): continue
        line = line.split()
        accts += line[-1:]

    for acct in accts:
        if(len([ex for ex in exclude['acct'] if (acct.find(ex) != -1)]) > 0): continue
        print "\chapter{" + acct + "}"

        subaccts = []
        output = runledger(commands['retrospective'] + ["^"+acct])
        for line in output.split('\n'):
            if(line == ""): continue
            subaccts += line.split(acct)[-1:]

        #Remove the starting ":" from the subaccount name
        subaccts = [subacct[1:] for subacct in subaccts]

        #Determine which accounts are excluded before iterating
        excluded = [subacct for ex in exclude['retrospective'] for subacct in subaccts if (str(acct + ":" + subacct).find(ex) != -1)]
        subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

        for subacct in subaccts:
            fullname = acct + ":" + subacct
            #print retrospective of subaccts with at least 7 transactions when viewed weekly over the last 12 months
            output = runledger(commands['last12months'] + ['-J', 'register'] + ["^" + fullname])
            if(len(output.split('\n')) < 6): continue

            print "\section{" + subacct + " Retrospective}"

            safename = fullname
            safename = safename.replace(' ', '')
            plot.main("../build/" + safename, commands['last12months'] + ['-J', 'register'] + ["^" + fullname])
            print "\insertplot{" + safename + "}"

        #identify budgeted subaccts
        subaccts = []
        output = runledger(commands['acctbudget'] + ["^"+acct])
        for line in output.split('\n'):
            if(line == ""): continue
            subaccts += line.split(acct)[-1:]

        #Remove the starting ":" from the subaccount name
        subaccts = [subacct[1:] for subacct in subaccts]

        #Determine which accounts are excluded before iterating
        excluded = [subacct for ex in exclude['forecast'] for subacct in subaccts if (str(acct + ":" + subacct).find(ex) != -1)]
        subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

        for subacct in subaccts:
            fullname = acct + ":" + subacct
            #print forecast of budgeted accts
            print "\section{" + subacct + " Forecast}"

            safename = fullname
            safename = safename.replace(' ', '')
            plot.main("../build/" + safename, commands['next12months'] + ['-J', 'register'] + ["^" + fullname])
            print "\insertplot{" + safename + "}"

    print summary

    print r"""\end{document}"""



summary = r"""
\chapter{Summary}

\begin{itemize}

\item The balance of my assets to my liabilities gives my net worth (including retirement funds): """ + runledger(commands['networth']).replace("Assets", "").strip() + """
\item Removing long term investment and loan accounts gives my net liquidity: """ + runledger(commands['networth']).replace("Assets", "").strip() + """
\item Balancing expenses against income yields your cash flow, or net profit/loss(negative is profit, positive is loss): """ + runledger(commands['networth']).replace("Assets", "").strip() + """

\end{itemize}
"""



header = r"""
\documentclass[pdftex,12pt,letterpaper]{report}
\usepackage[pdftex]{graphicx}
\usepackage[us, 12hr]{datetime}
\usepackage{verbatim}
\usepackage{moreverb}
\usepackage{hyperref}
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

