import os

def dir_scan(recursive_dir): #possibly divide into multiple fucntions
    """
    Searches through entire directory tree recursively
    Saves file info in a dict sorted by user
    """
    if os.path.isdir(recursive_dir):
        content_list = os.listdir(recursive_dir)
        for i in content_list:
            current_path = recursive_dir + '/' + i
            if os.path.isfile(current_path): #If dir is a file, check when it was modified
                yield current_path
            elif os.path.ismount(current_path):
                pass
            else:
                yield from dir_scan(current_path)
    else:
        raise OSError

if __name__ == '__main__':
    for path in dir_scan("/disk/scratch"):
        print(path)

