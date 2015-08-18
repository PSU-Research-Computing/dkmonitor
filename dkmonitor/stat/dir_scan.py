import os

def dir_scan(recursive_dir): #possibly divide into multiple fucntions
    """
    Searches through entire directory tree recursively
    Saves file info in a dict sorted by user
    """
    if os.path.isdir(recursive_dir):
        try:
            content_list = os.listdir(recursive_dir)
            for i in content_list:
                current_path = recursive_dir + '/' + i
                if os.path.isfile(current_path): #If dir is a file, check when it was modified
                    yield current_path
                elif os.path.isdir(current_path):
                    yield from dir_scan(current_path)
                else:
                    pass
        except PermissionError:
            pass
    else:
        print (recursive_dir)
        raise OSError

if __name__ == '__main__':
    for path in dir_scan("/disk/scratch"):
        print(path)

