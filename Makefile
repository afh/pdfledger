default:
	@pdflatex --enable-write18 -shell-escape pdfledger.tex 
#@cp pdfledger.pdf /Users/bettse/Dropbox/Virtual\ Filing\ Cabinet/Bank/

clean:
	rm *.txt
	rm *.log
	rm *.png
	rm *.aux
	rm *.pdf
