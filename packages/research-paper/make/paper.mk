# paper.mk — Shared Make targets for LaTeX papers across models.
#
# Usage in a model's paper/Makefile:
#   include $(shell git rev-parse --show-toplevel)/packages/research-paper/make/paper.mk
#
# Variables (override in the including Makefile if needed):
#   PAPER     main .tex basename (default: main)
#   TECTONIC  tectonic binary (default: tectonic)

PAPER    ?= main
TECTONIC ?= tectonic

REPO_ROOT           := $(shell git rev-parse --show-toplevel)
RESEARCH_PAPER_ROOT := $(REPO_ROOT)/packages/research-paper

# Tectonic looks for additional .cls/.sty/.bib via -Z search-path.
# latexmk/TeX Live honour TEXINPUTS/BIBINPUTS, so we export those too
# for users who prefer those tools.
export TEXINPUTS := .:$(RESEARCH_PAPER_ROOT)/latex//:
export BIBINPUTS := .:$(RESEARCH_PAPER_ROOT)/bib//:
export BSTINPUTS := .:$(RESEARCH_PAPER_ROOT)/latex//:

TECTONIC_FLAGS ?= --synctex --keep-logs \
                  -Z search-path=$(RESEARCH_PAPER_ROOT)/latex \
                  -Z search-path=$(RESEARCH_PAPER_ROOT)/bib

.PHONY: paper paper-clean paper-print-paths

paper:
	$(TECTONIC) $(TECTONIC_FLAGS) $(PAPER).tex

paper-clean:
	rm -f $(PAPER).pdf $(PAPER).log $(PAPER).aux $(PAPER).bbl \
	      $(PAPER).blg $(PAPER).out $(PAPER).toc $(PAPER).synctex.gz \
	      $(PAPER).fls $(PAPER).fdb_latexmk

paper-print-paths:
	@echo "REPO_ROOT           = $(REPO_ROOT)"
	@echo "RESEARCH_PAPER_ROOT = $(RESEARCH_PAPER_ROOT)"
	@echo "TEXINPUTS           = $$TEXINPUTS"
	@echo "BIBINPUTS           = $$BIBINPUTS"
