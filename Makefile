.PHONY: help install check test clean

PACKAGES := $(patsubst %/Makefile,%,$(wildcard packages/*/Makefile))
MODELS   := $(patsubst %/Makefile,%,$(wildcard models/*/Makefile))
ALL      := $(PACKAGES) $(MODELS)

help:
	@echo "Workspace commands:"
	@echo "  install   Install all workspace dependencies and git hooks"
	@echo "  check     Lint + type-check all packages"
	@echo "  test      Run all package tests"
	@echo "  clean     Remove build artifacts across packages"

install:
	@for d in $(ALL); do echo ">>> $$d" && $(MAKE) -C $$d dev; done
	pre-commit install

check:
	@for d in $(ALL); do echo ">>> $$d" && $(MAKE) -C $$d check; done

test:
	@for d in $(ALL); do echo ">>> $$d" && $(MAKE) -C $$d test; done

clean:
	@for d in $(ALL); do $(MAKE) -C $$d clean; done