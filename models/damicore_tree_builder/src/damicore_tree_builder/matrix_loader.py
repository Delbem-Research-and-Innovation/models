"""
Distance matrix loader module.

This module provides the MatrixLoader class, responsible for reading a
distance matrix from a CSV file and validating its structure before it is
used by the Neighbor-Joining algorithm.

The expected CSV format contains object names both in the first row and
in the first column. The remaining values represent pairwise distances
between the objects.

Example:

,80001.txt,80002.txt,80003.txt
80001.txt,0.0,0.95,0.88
80002.txt,0.95,0.0,0.94
80003.txt,0.88,0.94,0.0
"""

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

DEFAULT_INPUT_PATH = "models/fixtures/distance-matrix-output.csv"
DEFAULT_OUTPUT_PATH = "damicore_tree_builder/output/tree-output.nwk"