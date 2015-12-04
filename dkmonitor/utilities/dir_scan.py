"""
This file is a single function that yeilds every file in a directory tree
"""

import os

def dir_scan(recursive_dir): #possibly divide into multiple fucntions
    """
    Searches through entire directory tree recursively
    """
    try:
        content_list = os.listdir(recursive_dir)
        for path in content_list:
            current_path = os.path.join(recursive_dir, path)
            if os.path.isfile(current_path):
                yield current_path
            elif os.path.isdir(current_path):
                yield from dir_scan(current_path)
            else:
                pass
    except PermissionError:
        pass

