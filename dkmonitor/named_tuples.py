"""Contains named tuples used in other files"""

from collections import namedtuple

FileTuple = namedtuple('FileTuple', 'file_path file_size last_access')
StatTuple = namedtuple('StatTuple', 'total_file_size last_access_average')
