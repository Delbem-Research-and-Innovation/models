import os


def _get_files_from_directory(path: str) -> list[str]:
    """
    Get a list of file names from a directory.

    Parameters
    ----------
    path : str
        The path to the directory to list files from.

    Returns
    -------
    list[str]
        List of file names in the directory.

    Raises
    ------
    ValueError
        If the path does not exist.
    """
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist.")

    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def _get_file_data(file_path: str) -> bytes:
    """
    Get the data from a file as bytes.

    Parameters
    ----------
    file_path : str
        The path to the file to read.

    Returns
    -------
    bytes
        The file data as bytes.

    Raises
    ------
    ValueError
        If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File '{file_path}' does not exist.")

    with open(file_path, "rb") as f:
        return f.read()