#!/usr/bin/env bash
# new-paper.sh — Scaffold a new paper/ directory inside a model.
#
# Usage:
#   packages/research-paper/scripts/new-paper.sh <model-name>
#
# Example:
#   packages/research-paper/scripts/new-paper.sh damicore-clusterizer
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <model-name>" >&2
  exit 1
fi

MODEL="$1"
REPO_ROOT="$(git rev-parse --show-toplevel)"
TEMPLATE="$REPO_ROOT/packages/research-paper/templates/paper"
TARGET="$REPO_ROOT/models/$MODEL/paper"

if [[ ! -d "$REPO_ROOT/models/$MODEL" ]]; then
  echo "Error: model '$MODEL' not found at models/$MODEL" >&2
  exit 1
fi

if [[ -e "$TARGET" ]]; then
  echo "Error: $TARGET already exists" >&2
  exit 1
fi

cp -r "$TEMPLATE" "$TARGET"
echo "Created $TARGET"
echo "Next steps:"
echo "  cd models/$MODEL/paper"
echo "  make paper"
