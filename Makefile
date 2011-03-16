LATEX="xelatex"
LEDGER="templates/afh/pdfledger.tex"
CABINET="/Users/bettse/Dropbox/Virtual Filing Cabinet/"

bettse : LEDGER="templates/bettse/pdfledger.tex"
bettse : LATEX="pdflatex"

default:
	@$(LATEX) --enable-write18 -shell-escape --output-directory=build $(LEDGER)

bettse: file

file: default
	@cp build/pdfledger.pdf $(CABINET)/Bank

clean:
	rm -f build/*
