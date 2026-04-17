# research-paper

Shared LaTeX infrastructure for scientific papers in this monorepo.

Each model under `models/<name>/` can have its own `paper/` directory
authored in LaTeX, sharing a common class, macros, build config, and CI
workflow provided here.

## What this package provides

- `latex/model-paper.cls` — LaTeX class inherited by every paper.
- `latex/model-commands.sty` — common macros (`\todo`, `\figref`, …).
- `make/paper.mk` — Make targets (`paper`, `paper-clean`) reused by each model.
- `templates/paper/` — scaffold copied when creating a new paper.
- `scripts/new-paper.sh` — helper to bootstrap a paper inside a model.
- `../../.github/workflows/build-paper.yml` — reusable GitHub Actions
  workflow that compiles a paper with Tectonic and uploads the PDF.

## Creating a new paper for a model

```bash
make -C packages/research-paper new-paper MODEL=damicore-clusterizer
```

This creates `models/damicore-clusterizer/paper/` from the template.

## Building locally

Requires [Tectonic](https://tectonic-typesetting.github.io/) installed.

```bash
cd models/<model>/paper
make paper          # compiles main.tex -> main.pdf
make paper-clean    # removes build artefacts
```

Shared `.cls` / `.sty` / `.bib` files are located automatically via
`TEXINPUTS` / `BIBINPUTS` — nothing is copied into the model.

## CI

The `Papers` workflow (`.github/workflows/papers.yml`) detects changes under
`models/**/paper/**` or `packages/research-paper/**` and compiles the
affected papers, publishing each PDF as a build artefact.
