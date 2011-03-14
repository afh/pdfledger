LATEX="xelatex"
LEDGER="templates/afh/pdfledger.tex"
CABINET="/Users/bettse/Dropbox/Virtual\ Filing\ Cabinet/"

default:
	@$(LATEX) --enable-write18 -shell-escape --output-directory=build $(LEDGER)

file: default
	@cp build/pdfledger.pdf $(CABINET)/Bank

clean:
	rm -f build/*
