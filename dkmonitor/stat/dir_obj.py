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
                 datetime=None,
                 total_file_size=None,
                 use_percent=None,
                 use_percent_change=0.0,
                 average_access=None,
                 avrg_access_change=0.0):

        StatObj.__init__(self,
                         "directory_stats",
                         search_dir=search_dir,
                         system=system,
                         datetime=datetime,
                         total_file_size=total_file_size,
                         use_percent=use_percent,
                         use_percent_change=use_percent_change,
                         average_access=average_access,
                         avrg_access_change=avrg_access_change)

    def build_query_str(self):
        query_str = "searched_directory = '{searched_directory}' AND system = '{system}'"
        query_str.format(**self.collumn_dict)
        return query_str


