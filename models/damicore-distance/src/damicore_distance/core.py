import os

import numpy as np

from damicore_distance.compressors import Compressor, _get_compressed_size
from damicore_distance.io import _get_file_data, _get_files_from_directory


def _ncd(cx: int, cy: int, cxy: int) -> float:
    """Calculate Normalized Compression Distance (NCD).

    Parameters
    ----------
    cx : int
        Compressed size of file x.
    cy : int
        Compressed size of file y.
    cxy : int
        Compressed size of concatenated files x and y.

    Returns
    -------
    float
        NCD value between 0 and 1, where lower values indicate higher similarity.
    """
    max_c = max(cx, cy)
    ncd = (cxy - min(cx, cy)) / max_c if max_c != 0 else 0

    return max(0.0, min(1.0, ncd))


def ncd_matrix(input_dir: str, compressor: Compressor, compression_level: int = 9):
    filenames = sorted(_get_files_from_directory(input_dir))
    files = [os.path.join(input_dir, f) for f in filenames]
    n = len(files)

    matrix = np.zeros((n, n), dtype=np.float32)

    x_sizes = [
        _get_compressed_size(_get_file_data(file), compressor, compression_level)
        for file in files
    ]

    for x in range(n):
        for y in range(x + 1, n):
            file_x, file_y = files[x], files[y]
            c_xy = _get_compressed_size(
                _get_file_data(file_x) + _get_file_data(file_y),
                compressor,
                compression_level,
            )

            ncd = _ncd(x_sizes[x], x_sizes[y], c_xy)
            matrix[x][y] = ncd
            matrix[y][x] = ncd

    return matrix
