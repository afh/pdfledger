function plotbalance {
    bank=$1
    shift
    (cat <<EOF; ledger "$@") | gnuplot
        set terminal latex
        set output "${bank}balance.tex"
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%d"
        plot "-" using 1:2 title "USD" with lines
EOF
}

function plotforecast {
    bank=$1
    shift
    (cat <<EOF; ledger "$@") | gnuplot
        set terminal latex
        set output "${bank}forecast.tex"
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%b"
        plot "-" using 1:2 title "USD" with lines
EOF
}

#There are used to produce text output that will be verbatim included in the report
ledger -w -c -E -p "this month" --budget -M bal ^exp liab investment > budget.txt 
ledger --sort d -d "d>[today]-7" -c reg "^Assets:Bank:OSUFed:Checking$" > OSUtrans.txt
ledger --sort d -d "d>[today]-7" -c reg "^Assets:Bank:FirstTech:Checking$" > firsttrans.txt
ledger --forecast "d<=[today]+365" -d "d>[today] & d<[today]+365" --sort d reg "OSUFed:Checking" > OSUforecast.txt
ledger --forecast "d<=[today]+365" -d "d>[today] & d<[today]+365" --sort d reg "FirstTech:Checking" > FirstTechforecast.txt
ledger -w -c bal assets > assets.txt
ledger -w -c bal liabilities > liabilities.txt
ledger -c bal ^assets ^liab | tail -n1 > networth.txt
ledger -c bal ^liab ^assets and not roth | tail -n1 > liquidity.txt
ledger -c bal ^exp ^inc | tail -n1 > cashflow.txt


#These are used to produce data files for producing charts
plotbalance OSUmonth -J -c -p "daily" -d "d>=[this month] & d < [next month]"  --sort d reg "OSUFed:Checking"
plotbalance OSUyear -J -c --weekly -d "d<=[today] & d > [today]-365" --sort d reg "OSUFed:Checking"
plotbalance FirstTechmonth -J -c -p "daily" -d "d>=[this month] & d < [next month]"  --sort d reg "FirstTech:Checking"
plotbalance FirstTechyear -J -c --weekly -d "d<=[today] & d > [today]-365" --sort d reg "FirstTech:Checking"

plotforecast OSU -J -w --forecast "d<=[today]+365" -d "d>=[next month] & d<=[today]+365" --sort d reg "OSUFed:Checking" 
plotforecast FirstTech -J -w --forecast "d<=[today]+365" -d "d>=[next month] & d<=[today]+365" --sort d reg "FirstTech:Checking" 
ledger -w -c -F "%(account)\t%(total)\n" -p "this month" bal ^exp | sed -e 's/\$//g' | sed -e 's/,//g' | grep -P -v "(Expenses\t|Expenses:Bills\t|Expenses:Food\t|^\t|\.\t)" > month_breakdown.txt
python month_breakdown.py

