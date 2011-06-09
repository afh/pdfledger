#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import re
import sys
import pie
import boxplot
import plot
import codecs
import getpass
import pystache
import ConfigParser
from subprocess import Popen,PIPE

config = ConfigParser.RawConfigParser()
config.read('./examples/pdfledger.cfg')

user = ""
if len(sys.argv) > 1:
    user = sys.argv[1]
else:
    user = getpass.getuser().strip()
    #print "No user provided, using ", user

commands = {}
commands['accts'] = ['--collapse', '--no-total', '--basis', 'balance']
commands['acctbudget'] = ['-E', '--flat', '--budget', '--no-total', 'balance']
commands['budget'] = ['--flat', '--no-total', '-p', 'this month', 'budget']
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
commands['next12months'] += config.get(user, 'exchange').split(' ')
commands['last12months'] += config.get(user, 'exchange').split(' ')
#print "Exclude: ", exclude
#print "Commands: ", commands

def tail(input):
    if(input[-1] == '\n'):
        input = input[:-1]
    input = input.split("\n")
    return unicode(' '.join(input[-1:])).strip()


def runledger(parameters):
    command = ["ledger", '-f', LEDGER_FILE, '-c'] + parameters
    #print ' '.join(command)
    output = Popen(command, stdout=PIPE).communicate()[0]
    if(len(output) > 0 and output[-1] == '\n'):
        return unicode(output[:-1], 'UTF')
    else:
        return unicode(output, 'UTF')

def safe_name(safename):
    safename = re.sub('[ :]', '', safename)
    safename = re.sub(u'ä', 'ae', safename)
    safename = re.sub(u'ü', 'ue', safename)
    safename = re.sub(u'ö', 'oe', safename)
    safename = re.sub(u'ß', 'ss', safename)
    safename = re.sub(u'Ä', 'Ae', safename)
    safename = re.sub(u'Ü', 'Ue', safename)
    safename = re.sub(u'Ö', 'Oe', safename)
    return safename

def retrospective(acct):
    rtnstring = ""
    subaccts = []
    output = runledger(commands['retrospective'] + ["^"+acct])
    for line in output.split('\n'):
        subaccts += line.split(acct)[-1:]

    #Remove the starting ":" from the subaccount name
    subaccts = [subacct[1:] for subacct in subaccts]

    #Determine which accounts are excluded before iterating
    excluded = [subacct for ex in exclude['retrospective'] for subacct in subaccts if (unicode(acct + ":" + subacct).find(ex) != -1)]
    subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

    retro = []
    for subacct in subaccts:
        fullname = acct + ":" + subacct
        #print retrospective of subaccts with at least 7 transactions when viewed weekly over the last 12 months
        output = runledger(commands['last12months'] + ['-J', 'register'] + ["^" + fullname])
        if(len(output.split('\n')) < 6): continue

        safename = safe_name(fullname)
        plot.main("./build/" + safename + "retro", commands['last12months'] + ['-J', 'register'] + ["^" + fullname] + ["-f", LEDGER_FILE])
        retro.append({'name': subacct, 'plotfile': safename + "retro"})
    return retro

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
    excluded = [subacct for ex in exclude['forecast'] for subacct in subaccts if (unicode(acct + ":" + subacct).find(ex) != -1)]
    subaccts = [subacct for subacct in subaccts if (subacct not in excluded)]

    forecast = []
    for subacct in subaccts:
        fullname = acct + ":" + subacct
        safename = safe_name(fullname)
        file = "./build/" + safename + "forecast"
        args = commands['next12months'] + ['-J', 'register'] + ["^" + fullname] + ["-f", LEDGER_FILE]
        #print file, ' ', ' '.join(args)
        plot.main(file, args)
        #forecast.append({'name': subacct, 'plotfile': safename + "forecast"})

    return forecast


def main():
    mustache = {
      'accounts': [],
      'networth': tail(runledger(commands['networth'])).replace("Assets", ""),
      'liquidity': tail(runledger(commands['liquidity'])).replace("Assets", ""),
      'cashflow': tail(runledger(commands['cashflow']))
    }

    pie.main("./build/", ['-f', LEDGER_FILE, 'balance', '--basis', config.get(user, 'expenses_acct')])
    boxplot.main("./build/", ['-f', LEDGER_FILE])
    if(config.getboolean(user, 'budget')):
        mustache['budget'] = runledger(commands['budget'])

    output = runledger(commands['accts'])
    accts = []
    for line in output.split('\n'):
        line = line.split()
        accts += line[-1:]

    for acct in accts:
        if(len([ex for ex in exclude['acct'] if (acct.find(ex) != -1)]) > 0): continue

        account_data = {
          'name': unicode(acct),
          'retrospectives': retrospective(acct)
        }

        if(config.getboolean(user, 'budget')):
          account_data['forecasts'] = forecast(acct)

        mustache['accounts'].append(account_data)

    template_file = codecs.open(config.get(user, 'template_file'), encoding='utf-8', mode='r')
    template_data = "".join(template_file.readlines())
    template_file.close()
    tex_file = codecs.open('build/pdfledger.tex', encoding='utf-8', mode='w')
    tex_file.write(pystache.render(template_data, mustache))
    tex_file.close()

if __name__ == "__main__":
    main()

