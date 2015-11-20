import argparse

import sys, os
sys.path.append(os.path.abspath(".."))

from dkmonitor.monitor_manager import main as monitor_main
from dkmonitor.config.task_manager import main as task_main
from dkmonitor.admin_interface import main as admin_main


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    description = ""
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(which="run")
    view_parser = subparsers.add_parser("view")
    view_parser = view_parser.set_defaults(which="view")
    task_parser = subparsers.add_parser("task")
    task_parser = task_parser.set_defaults(which="task")

    try:
        parsed_arg = parser.parse_args([args[0]])
        which = parsed_arg.which
        if which == "run":
            monitor_main(args[1:])
        elif which == "view":
            admin_main(args[1:])
        elif which == "task":
            task_main(args[1:])
    except IndexError:
        print("First argument required (run, view, task)", file=sys.stderr)


if __name__ == "__main__":
    main()
