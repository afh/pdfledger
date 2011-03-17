LATEX="xelatex"
LEDGER="templates/afh/pdfledger.tex"
CABINET="/Users/bettse/Dropbox/Virtual Filing Cabinet/"

USER=$(shell whoami)
ifeq '$(USER)' 'bettse'
LEDGER="build/pdfledger.tex"
LATEX="pdflatex"
endif

default:
	@$(LATEX) --enable-write18 -shell-escape --output-directory=build $(LEDGER)

file: default
	@cp build/pdfledger.pdf $(CABINET)/Bank

clean:
	rm -f build/*
