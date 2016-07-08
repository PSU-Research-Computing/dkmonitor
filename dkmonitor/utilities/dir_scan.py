"""
Single function that yeilds every file in a directory tree
"""

import os

def dir_scan(base_dir):
    """
    Returns every file path in a directory tree

    **Wrapper function for dir_scan_generator that throws a permissions
    error if base_dir's permisssions are incorrect

    INPUT: path to a directory to scan
    OUTPUT: Generator object that yeild all file paths in a direcotry
    """
    def dir_scan_generator(base_dir):
        """Return every file in a directory tree"""
        try:
            content_list = os.listdir(base_dir)
            for path in content_list:
                current_path = os.path.join(base_dir, path)
                if os.path.isfile(current_path):
                    yield current_path
                elif os.path.isdir(current_path):
                    yield from dir_scan_generator(current_path)
                else:
                    pass
        except PermissionError:
            pass

    #TODO better error catching
    if os.access(base_dir, os.R_OK) is True:
        return dir_scan_generator(base_dir)
    else:
        raise PermissionError
