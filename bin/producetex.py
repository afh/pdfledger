#!/usr/bin/env python
from subprocess import Popen,PIPE
import sys
import plot
print r"""
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

LEDGER_FILE="/Users/bettse/Dropbox/Finances/201103.lgr"
if len(sys.argv) > 1:
    LEDGER_FILE = sys.argv[1]

ledger = ["ledger", '-f', LEDGER_FILE, '-c']

commands = {}
commands['accts'] = ['--collapse', '--no-total', 'balance']
commands['budget'] = ['--flat', '--budget', '--no-total', 'balance']
commands['retrospective'] = ['--flat', '--no-total', 'balance']
commands['last12months'] = ['-d', '"d<[today] & d>[today]-365"', '--sort', 'd', '--weekly']
commands['next12months'] = ['-d', '"d>[today] & d<[today]+365"', '--sort', 'd', '--weekly']

output = Popen(ledger + commands['accts'], stdout=PIPE).communicate()[0]
accts = []
for line in output.split('\n'):
    if(line == ""): continue
    line = line.split()
    accts += line[-1:]

for acct in accts:
    print "\chapter{" + acct + "}"

    subaccts = []
    output = Popen(ledger + commands['retrospective'] + ["^"+acct], stdout=PIPE).communicate()[0]
    for line in output.split('\n'):
        if(line == ""): continue
        subaccts += line.split(acct)[-1:]

    for subacct in subaccts:
        #print retrospective of subaccts with at least 7 transactions when viewed weekly over the last 12 months
        output = Popen(ledger + commands['last12months'] + ['-J', 'register'] + ["^" + acct + subacct], stdout=PIPE).communicate()[0]
        if(len(output.split('\n')) < 6): continue

        print "\section{" + subacct[1:] + " Retrospective}"
        safename = acct+subacct
        safename = safename.replace(' ', '')
        plot.main("../build/" + safename, commands['last12months'] + ['-J', 'register'] + ["^" + acct + subacct])
        print "\insertplot{" + safename + "}"

    #identify budgeted subaccts

    #print forecast of budgeted accts

temp = """
\section{Current month progress}

Negative values indicate to-be-spent funds.  Positive vaues indicate overspending.

\verbatiminput{build/budget.txt}

\chapter{Assets}

\verbatiminput{build/assets.txt}

\chapter{Liabilities}

\verbatiminput{build/liabilities.txt}

\chapter{Transactions}

\section{First Tech Credit Union}

Balance over the last year to date :

\insertplot{checking-1yearbalance}

Balance during \monthname :

\insertplot{checking-1monthbalance}

Transactions for the last 7 days:
"""
print r"""
\chapter{Summary}

\begin{itemize}

\item The balance of my assets to my liabilities gives my net worth (including retirement funds): \input{build/networth.txt}
\item Removing long term investment and loan accounts gives my net liquidity: \input{build/liquidity.txt}
\item Balancing expenses against income yields your cash flow, or net profit/loss(negative is profit, positive is loss): \input{build/cashflow.txt}

\end{itemize}
"""

print r"""\end{document}"""
