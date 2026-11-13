# Optional shortcuts; every target calls run_checks.py, which is what Windows users run directly
# (`python run_checks.py <step>`). Requires: pip install -r requirements.txt ; pdflatex + bibtex for `make paper`.
# Usage: make numbers | certificates | map | bias | learning | paper | check | help

PYTHON ?= python

.PHONY: help numbers certificates map bias learning paper check

help:
	@echo "make numbers       - the guardian on both documents: every printed number against its stored source (seconds; 0 MISSING expected)"
	@echo "make certificates  - exact verification of a sample of 5 certificates (about 2 minutes; all: python run_checks.py certificates --all)"
	@echo "make map           - the declared map code on the public data, compared with the stored outputs by SHA-256 (3 to 6 minutes)"
	@echo "make bias          - the declared tests of the bias on the public labels, compared (seconds)"
	@echo "make learning      - the cheap stage of the learning tests, compared (about 2 minutes)"
	@echo "make paper         - pdflatex + bibtex of main.tex, supplement.tex and tables.tex into a temporary folder"
	@echo "make check         - all of the above"

numbers:
	$(PYTHON) run_checks.py numbers

certificates:
	$(PYTHON) run_checks.py certificates

map:
	$(PYTHON) run_checks.py map

bias:
	$(PYTHON) run_checks.py bias

learning:
	$(PYTHON) run_checks.py learning

paper:
	$(PYTHON) run_checks.py pdf --keep

check:
	$(PYTHON) run_checks.py
