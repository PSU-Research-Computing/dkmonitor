"""
Single function that yeilds every file in a directory tree
"""

import os

def dir_scan(recursive_dir):
    """
    Wrapper function for dir_scan_recursive that throws permission error
    if permisssions are incorrect
    """
    def dir_scan_generator(recursive_dir):
        """Searches through entire directory tree recursively"""
        try:
            content_list = os.listdir(recursive_dir)
            for path in content_list:
                current_path = os.path.join(recursive_dir, path)
                if os.path.isfile(current_path):
                    yield current_path
                elif os.path.isdir(current_path):
                    yield from dir_scan_generator(current_path)
                else:
                    pass
        except PermissionError:
            pass

    if os.access(recursive_dir, os.R_OK) is True:
        return dir_scan_generator(recursive_dir)
    else:
        raise PermissionError


