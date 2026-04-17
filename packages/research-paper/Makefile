.PHONY: dev check test clean new-paper

dev:
	@if command -v tectonic > /dev/null 2>&1; then \
		echo "tectonic already installed: $$(command -v tectonic)"; \
	else \
		echo "Installing tectonic..."; \
		curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh; \
		mkdir -p ~/.local/bin && mv tectonic ~/.local/bin/tectonic; \
		echo "tectonic installed at ~/.local/bin/tectonic"; \
		echo "Make sure ~/.local/bin is in your PATH."; \
	fi

check:
	@echo "No automated checks yet."

test:
	@echo "No tests."

clean:
	@true

new-paper:
ifndef MODEL
	$(error Usage: make -C packages/research-paper new-paper MODEL=<model-name>)
endif
	@./scripts/new-paper.sh $(MODEL)
