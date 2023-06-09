import os
import shutil
from pathlib import Path
from typing import Any, Union

# See: https://stackoverflow.com/a/59313490/9045426
PathLike = Union[str, bytes, os.PathLike[Any]]


def copy_file(src: PathLike, dst: PathLike) -> Path:
    """
    Copy a file with path `src` to `dst`. If the parent directory of the destination file does not
    exist, create it. Return the path to the copied file.
    """
    os.makedirs(os.path.dirname(src), exist_ok=True)
    return shutil.copy(src, dst)
