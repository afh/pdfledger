LATEX="xelatex"
PDFLEDGER="templates/afh/pdfledger.tex"
CABINET="/Users/bettse/Dropbox/Virtual Filing Cabinet/"
BUILD="build"

ifeq '${USER}' 'bettse'
LATEX="pdflatex"
PDFLEDGER="$(BUILD)/pdfledger.tex"
endif

default: genlatex
	@$(LATEX) --enable-write18 -shell-escape --output-directory=build $(BUILD)/pdfledger.tex

genlatex:
	@./bin/genlatex.py

file: default
	@cp $(BUILD)/pdfledger.pdf $(CABINET)/Bank

init:
	mkdir -p $(BUILD)

clean:
	rm -f $(BUILD)/*
