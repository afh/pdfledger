#!/bin/sh

config=$1
ledgerfile=$2

bin=`dirname $0`
build=build
test -e $build || mkdir -p $build

. $config

function plotbalance {
    bank=$1
    currency=EUR # USD
    shift
    (cat <<EOF; ledger "$@") | LC_ALL=de_DE gnuplot
        set terminal latex
        set output "${build}/${bank}balance.tex"
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%d"
        plot "-" using 1:2 title "${currency}" with lines
EOF
}

function plotforecast {
    bank=$1
    currency=EUR # USD
    shift
    (cat <<EOF; ledger "$@") | LC_ALL=de_DE gnuplot
        set terminal latex
        set output "${build}/${bank}forecast.tex"
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%b"
        plot "-" using 1:2 title "${currency}" with lines
EOF
}

#These are used to produce text output that will be verbatim included in the report
ledger -f "${ledgerfile}" -w -c -E -p "this month" --budget -M bal $budget_accounts > $build/budget.txt
ledger -f "${ledgerfile}" --sort d -d "d>[today]-7" -c reg $checking_1 > $build/checking-1trans.txt
ledger -f "${ledgerfile}" --sort d -d "d>[today]-7" -c reg $checking_2 > $build/checking-2trans.txt
ledger -f "${ledgerfile}" --forecast "d<=[today]+365" -d "d>[today] & d<[today]+365" --sort d reg $checking_1_forecast | sed -e 's/Forecast transaction/Prognose/' > $build/checking-1forecast.txt
ledger -f "${ledgerfile}" --forecast "d<=[today]+365" -d "d>[today] & d<[today]+365" --sort d reg $checking_1_forecast > $build/checking-2forecast.txt
ledger -f "${ledgerfile}" -w -c bal $assets_account > $build/assets.txt
ledger -f "${ledgerfile}" -w -c bal $liabilities_account > $build/liabilities.txt
ledger -f "${ledgerfile}" -c bal ^$assets_account ^$liabilities_account | tail -n1 > $build/networth.txt
ledger -f "${ledgerfile}" -c bal ^$liabilities_account ^$assets_account $liquidity_exclude | tail -n1 > $build/liquidity.txt
ledger -f "${ledgerfile}" -c bal ^$expenses_account ^$cashflow_inc_account | tail -n1 > $build/cashflow.txt

#These are used to produce data files for producing charts
plotbalance "checking-1month" -f "${ledgerfile}" -J -c -p "daily" -d "d>=[this month] & d < [next month]"  --sort d reg $checking_1_forecast
plotbalance "checking-1year" -f "${ledgerfile}" -J -c --weekly -d "d<=[today] & d > [today]-365" --sort d reg $checking_1_forecast
plotbalance "checking-2month" -f "${ledgerfile}" -J -c -p "daily" -d "d>=[this month] & d < [next month]"  --sort d reg $checking_2_forecast
plotbalance "checking-2year" -f "${ledgerfile}" -J -c --weekly -d "d<=[today] & d > [today]-365" --sort d reg $checking_2_forecast

plotforecast "checking-1" -f "${ledgerfile}" -J -w --forecast "d<=[today]+365" -d "d>=[next month] & d<=[today]+365" --sort d reg $checking_1_forecast
plotforecast "checking-2" -f "${ledgerfile}" -J -w --forecast "d<=[today]+365" -d "d>=[next month] & d<=[today]+365" --sort d reg $checking_2_forecast

ledger -f "${ledgerfile}" -w -c -F "%(account)\t%(total)\n" -p "this month" bal ^$expenses_account \
  | sed -e 's/[€\$]//g' -e 's/,/./g' \
  | grep -P -v $month_grep_v \
  > $build/month_breakdown.txt

python $bin/month_breakdown.py $build/month_breakdown.txt

