import argparse

import sys, os
sys.path.append(os.path.abspath(".."))

from dkmonitor.monitor_manager import main as monitor_main
from dkmonitor.config.task_manager import main as task_main
from dkmonitor.stat_viewer import main as admin_main
from dkmonitor.utilities.database_interface import main as data_main

def description():
    return ("dkmonitor is a disk monitoring utility used to monitor, record and notify ",
            "idividual user's usage statistics on a shared storage space")

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=description())

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(which="run")

    view_parser = subparsers.add_parser("view")
    view_parser.set_defaults(which="view")

    task_parser = subparsers.add_parser("task")
    task_parser.set_defaults(which="task")

    data_parser = subparsers.add_parser("database")
    data_parser.set_defaults(which="database")

    try:
        parsed_arg = parser.parse_args([args[0]])
        if parsed_arg.which == "run":
            monitor_main(args[1:])
        elif parsed_arg.which == "view":
            admin_main(args[1:])
        elif parsed_arg.which == "task":
            task_main(args[1:])
        elif parsed_arg.which == "database":
            data_main(args[1:])
    except IndexError:
        print("First argument required (run, view, task, database)", file=sys.stderr)


if __name__ == "__main__":
    main()
