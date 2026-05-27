"""Command-line interface for multimap_map_selector.

Usage examples:

  # single file
  python3 -m multimap_map_selector.cli --input path/to/file.csv --output outdir

  # batch directory (process all .csv files)
  python3 -m multimap_map_selector.cli --input path/to/dir --output outdir --batch

This wraps `recommend_visualization_spec` to provide a one-command runner.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .types import RecommenderStrategy
from . import recommend_visualization_spec


def iter_csvs(path: Path) -> Iterable[Path]:
    if path.is_dir():
        for p in sorted(path.glob('*.csv')):
            yield p
    else:
        yield path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog='multimap-map-selector')
    p.add_argument('--input', '-i', required=True, help='Input CSV file or directory')
    p.add_argument('--output', '-o', default=None, help='Output directory for spec JSONs')
    p.add_argument('--batch', action='store_true', help='Process directory as batch')
    p.add_argument('--target-library', default='geovis', help='Target library (informational)')
    args = p.parse_args(argv)

    inp = Path(args.input)
    out = Path(args.output) if args.output else None
    strategy = RecommenderStrategy(target_library=args.target_library, fallback_map='base_map')

    files = list(iter_csvs(inp)) if args.batch or inp.is_dir() else [inp]
    if not files:
        print('No CSV files found at', inp)
        return 2

    for f in files:
        try:
            result = recommend_visualization_spec(f, strategy, output_directory=out)
        except Exception as exc:
            print(f.name, '-> error:', type(exc).__name__, exc)
            continue
        if result.status == 'success':
            spec = result.visualization_spec
            layer = spec.get('layer_type') if isinstance(spec, dict) else None
            print(f.name, '->', result.status, 'layer:', layer, 'json:', result.output_spec_path)
        else:
            print(f.name, '->', result.status, 'reason:', result.visualization_spec.get('reason'))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
