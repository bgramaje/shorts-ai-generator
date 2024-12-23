import os
import shutil
from os.path import exists


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(dir) -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    if exists(dir):
        shutil.rmtree(dir)

        return 1
