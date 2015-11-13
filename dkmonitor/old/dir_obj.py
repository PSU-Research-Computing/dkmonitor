"""
This script is designed to collect data on an entire directory or disk
"""
import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.stat.stat_obj import StatObj

class Directory(StatObj):
    """Collects data on an entire directory"""

    def __init__(self,
                 search_dir=None,
                 system=None,
                 datetime=None):

        StatObj.__init__(self,
                         "directory_stats",
                         search_dir=search_dir,
                         system=system,
                         datetime=datetime)

    def build_query_str(self):
        query_str = "searched_directory = '{searched_directory}' AND system = '{system}'"
        query_str.format(**self.collumn_dict)
        return query_str


