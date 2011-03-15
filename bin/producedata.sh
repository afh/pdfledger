#!/bin/sh

config=$1
ledgerfile=$2

bin=`dirname $0`
build=build
test -e $build || mkdir -p $build

. $config

#These are used to produce text output that will be verbatim included in the report
ledger -f "${ledgerfile}" -c -E -p "this month" budget $budget_accounts > $build/budget.txt
ledger -f "${ledgerfile}" --sort d -d "d>[today]-7" -c reg $checking_1 > $build/checking-1trans.txt
ledger -f "${ledgerfile}" --forecast "d<=[today]+365" -d "d>[today] & d<[today]+365" --sort d reg $checking_1_forecast | sed -e 's/Forecast transaction/Prognose/' > $build/checking-1forecast.txt
ledger -f "${ledgerfile}" -w -c bal $assets_account > $build/assets.txt
ledger -f "${ledgerfile}" -w -c bal $liabilities_account > $build/liabilities.txt
ledger -f "${ledgerfile}" -c bal ^$assets_account ^$liabilities_account | tail -n1 > $build/networth.txt
ledger -f "${ledgerfile}" -c bal ^$liabilities_account ^$assets_account $liquidity_exclude | tail -n1 > $build/liquidity.txt
ledger -f "${ledgerfile}" -c bal ^$expenses_account ^$cashflow_inc_account | tail -n1 > $build/cashflow.txt

#These are used to produce data files for producing charts
python $bin/plot.py "${build}/${bank}checking-1monthbalance" -f "${ledgerfile}" -J -c -p "daily" -d "d>=[this month] & d < [next month]"  --sort d reg $checking_1_forecast
python $bin/plot.py "${build}/${bank}checking-1yearbalance" -f "${ledgerfile}" -J -c --weekly -d "d<=[today] & d > [today]-365" --sort d reg $checking_1_forecast

python $bin/plot.py "${build}/${bank}checking-1forecast" -f "${ledgerfile}" -J -w --forecast "d<=[today]+365" -d "d>=[next month] & d<=[today]+365" --sort d reg $checking_1_forecast

ledger -f "${ledgerfile}" -w -c -F "%(account)\t%(total)\n" -p "this month" bal ^$expenses_account \
  | sed -e 's/[€\$]//g' -e 's/,/./g' \
  | grep -P -v $month_grep_v \
  > $build/month_breakdown.txt

python $bin/month_breakdown.py $build/month_breakdown.txt

