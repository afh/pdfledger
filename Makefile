LATEX="xelatex"
PDFLEDGER="templates/afh/pdfledger.tex"
CABINET="/Users/bettse/Dropbox/Virtual Filing Cabinet/"

USER=$(shell whoami)
ifeq '$(USER)' 'bettse'
PDFLEDGER="build/pdfledger.tex"
LATEX="pdflatex"
endif

default:
	@$(LATEX) --enable-write18 -shell-escape --output-directory=build $(PDFLEDGER)

genlatex:
	@./bin/genlatex.py

file: default
	@cp build/pdfledger.pdf $(CABINET)/Bank

clean:
	rm -f build/*
