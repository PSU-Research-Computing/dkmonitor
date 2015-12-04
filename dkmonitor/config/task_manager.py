"""
This module deals with loading, modifying and displaying tasks
"""

import argparse
from sqlalchemy.exc import InvalidRequestError, DataError

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.database_manager import Tasks, DataBase
from dkmonitor.config.settings_manager import export_settings

class TaskDataBase(DataBase):
    """An interface used to create, display, edit, remove, and list tasks"""
    def __init__(self, db_settings):
        super().__init__(hostname=db_settings["hostname"],
                         database=db_settings["database"],
                         password=db_settings["password"],
                         username=db_settings["username"],
                         db_type=db_settings["db_type"])

    def remove_task(self, taskname):
        """Removes a task forthe database"""
        session = self.create_session()
        if session.query(Tasks).filter(Tasks.taskname == taskname).delete() == 1:
            session.commit()
            print("Task '{}' was deleted".format(taskname))
        else:
            print("Task '{}' does not exist".format(taskname), file=sys.stderr)

    def update_column(self, taskname, column_name, update_value):
        """Changes a column value in an existing row"""
        session = self.create_session()
        try:
            if session.query(Tasks).filter(Tasks.taskname == taskname).\
                                    update({column_name: update_value}) == 1:
                session.commit()
                print("Task: '{task}', column: '{cname}' was set to {val}".format(task=taskname,
                                                                                  cname=column_name,
                                                                                  val=update_value))
            else:
                print("Task '{}' does not exist".format(taskname))
        except InvalidRequestError:
            print("Column Name {} is invalid".format(column_name))
        except DataError:
            print("Value {} is incorrect type".format(update_value))

    def get_all_tasks(self):
        """Gets a list of all tasks"""
        session = self.create_session()
        tasks = session.query(Tasks).all()
        return tasks

    def get_task_info(self, taskname):
        """Gets a task row based on task name"""
        session = self.create_session()
        task = session.query(Tasks).filter(Tasks.taskname == taskname).all()
        task_info = {}
        try:
            task = task[0]
            for column in task.__table__.columns:
                task_info[column.name] = getattr(task, column.name)
            return task_info

        except IndexError:
            return None

    def display_task_info(self, taskname):
        """Displays task varibales to console based on a taskname"""
        task_info = self.get_task_info(taskname)
        display_format = """Task_Name: {taskname}
        Host_Name: {hostname}
        Target_Path: {target_path}
        Relocation_Path: {relocation_path}
        Delete_Old_Files: {delete_old_files}
        Delete_When_Full: {delete_when_full}
        Disk_Usage_Warning_Threshold: {usage_warning_threshold} %
        Disk_Usage_Critical_Threshold: {usage_critical_threshold} %
        Old_File_Threshold: {old_file_threshold} days
        Email_Usage_Warnings: {email_usage_warnings}
        Email_Data_Alerations: {email_data_alterations}
        Email_Top_Percent: {email_top_percent} %
        Enabled: {enabled}"""

        if task_info is not None:
            print(display_format.format(**task_info))
        else:
            print("Task '{}' does not exist".format(taskname), file=sys.stderr)

    def display_tasks(self):
        """Displays tasks nicely to the console"""
        session = self.create_session()
        tasks = [task for task in session.query(Tasks.taskname).distinct()]
        if tasks != []:
            print("Saved tasks:")
            for task in tasks:
                print(task[0])
        else:
            print("No tasks found", file=sys.stderr)


def parse_create_command(args):
    """Creates a new task from command line arguments"""
    new_task = Tasks(taskname=args.taskname,
                     hostname=args.hostname,
                     target_path=args.target_path,
                     relocation_path=args.relocation_path,
                     delete_old_files=args.delete_old_files,
                     delete_when_full=args.delete_when_full,
                     usage_warning_threshold=args.usage_warning_threshold,
                     usage_critical_threshold=args.usage_critical_threshold,
                     old_file_threshold=args.old_file_threshold,
                     email_usage_warnings=args.email_usage_warnings,
                     email_data_alterations=args.email_data_alterations,
                     email_top_percent=args.email_top_percent)
    return new_task

def creation_interface():
    """Captive interface for creating a new task"""
    task_input = {"taskname":"",
                  "hostname":"",
                  "target_path":"",
                  "disk_warning_threshold":0,
                  "disk_critical_threshold":0,
                  "relocation_path":"",
                  "delete_when_full":False,
                  "delete_old_files":False,
                  "old_file_threshold":0,
                  "email_usage_warnings":False,
                  "email_top_percent":0,
                  "email_data_alterations":False,
                  "enabled":True}

    task_input["taskname"] = input("Task name(unique): ")
    task_input["hostname"] = input("Target hostname: ")
    task_input["target_path"] = input("Target directory: ")
    task_input["disk_warning_threshold"] = read_percent(("Disk use warning "
                                                         "threshold(percent)(int): "))
    task_input["disk_critical_threshold"] = read_percent(("Disk use cirtical "
                                                          "threshold(percent)(int): "))

    relocate_old = read_bool(("Relocate old files when the disk"
                              "is over it's critical threshold?(y/n): "))
    if relocate_old is True:
        relocation_path = input("Relocation path: ")
        task_input["relocation_path"] = relocation_path
        task_input["delete_when_full"] = read_bool(("Delete files when relocation"
                                                    "path is full?(y/n): "))
    elif relocate_old is False:
        task_input["delete_old_files"] = read_bool("Delete old files?(y/n): ")

    if (relocate_old is True) or (task_input["delete_old_files"] is True):
        task_input["old_file_threshold"] = read_int("Old file threshold(days)(int): ")

    task_input["email_usage_warnings"] = read_bool(("Send emails when the disk is"
                                                    "over it's warning threshold?(y/n): "))

    if task_input["email_usage_warnings"] is True:
        task_input["email_top_percent"] = read_percent(("Percent of top users "
                                                        "to be emailed(percent)(int): "))

    if (relocate_old is True) or (task_input["delete_old_files"] is True):
        task_input["email_data_alterations"] = read_bool(("Send emails when data"
                                                          "has been altered?(y/n): "))

    task_input["enabled"] = read_bool("Would you like to enable this task?(y/n): ")

    new_task = Tasks(taskname=task_input["taskname"],
                     hostname=task_input["hostname"],
                     target_path=task_input["target_path"],
                     relocation_path=task_input["relocation_path"],
                     delete_old_files=task_input["delete_old_files"],
                     delete_when_full=task_input["delete_when_full"],
                     usage_warning_threshold=task_input["disk_warning_threshold"],
                     usage_critical_threshold=task_input["disk_critical_threshold"],
                     old_file_threshold=task_input["old_file_threshold"],
                     email_usage_warnings=task_input["email_usage_warnings"],
                     email_data_alterations=task_input["email_data_alterations"],
                     email_top_percent=task_input["email_top_percent"],
                     enabled=task_input["enabled"])
    return new_task

###UTILITY INPUT FUNCTIONS FOR CREATION INTERFACE###########
def read_int(question):
    """Reads an int, will not exit unless int is entered"""
    while True:
        raw_in = input(question)
        if raw_in.isdigit():
            return int(raw_in)
        else:
            print("Please enter an integer")

def read_percent(question):
    """Reads in a percent, will not exit unless value is between 1 and 100"""
    while True:
        raw_in = input(question)
        if (raw_in.isdigit()) and (int(raw_in) in range(100)):
            return int(raw_in)
        else:
            print("Please enter an integer between 1 and 100")


def read_bool(question):
    """Reads in boolean, will not exit unless y or n is entered"""
    while True:
        raw_in = input(question)
        if raw_in.lower() == 'y':
            return True
        elif raw_in.lower() == 'n':
            return False
        else:
            print("Please enter either 'y' or 'n'")
##############################################################

def export_tasks():
    """Exports tasks from database in a dictionary"""
    settings = export_settings()
    taskdb = TaskDataBase(settings["DataBase_Settings"])
    raw_tasks = taskdb.get_all_tasks()
    formatted_tasks = {}
    try:
        for task in raw_tasks:
            task_info = {}
            for column in task.__table__.columns:
                task_info[column.name] = getattr(task, column.name)
            formatted_tasks[task.taskname] = task_info

        return formatted_tasks
    except IndexError:
        return None

def get_args(args):
    """Defines arguments for command line"""
    description = ("This command line interface is used to interface"
                   " with the task database database of dkmonitor")
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers()
    create_interface_parser = subparsers.add_parser("creation_interface")
    create_interface_parser.set_defaults(which="creation_interface")

    create_command_parser = subparsers.add_parser("creation_command")
    create_command_parser.set_defaults(which="creation_command")
    create_command_parser.add_argument("--taskname",
                                       dest="taskname",
                                       required=True,
                                       help="Unique name of the task")
    create_command_parser.add_argument("--hostname",
                                       dest="hostname",
                                       required=True,
                                       help="Host name of the machine to run the task on")
    create_command_parser.add_argument("--target_path",
                                       dest="target_path",
                                       required=True,
                                       help="Path of disk/directory to monitor")

    file_management_group = create_command_parser.add_mutually_exclusive_group()
    file_management_group.add_argument("--relocation_path",
                                       dest="relocation_path",
                                       help="Path to relocate files to")
    file_management_group.add_argument("--delete_old_files",
                                       dest="delete_old_files",
                                       action="store_true",
                                       help="Delete old files when disk over critical")

    create_command_parser.add_argument("--delete_when_full",
                                       dest="delete_when_full",
                                       action="store_true",
                                       help="Delete files when the relocation path is full")
    create_command_parser.add_argument("--usage_warning_threshold",
                                       dest="usage_warning_threshold",
                                       type=int,
                                       required=True,
                                       help="Threshold when warnings should be sent out")
    create_command_parser.add_argument("--usage_critical_threshold",
                                       dest="usage_critical_threshold",
                                       type=int,
                                       required=True,
                                       help="Threshold when files should be moved/deleted")
    create_command_parser.add_argument("--old_file_threshold",
                                       dest="old_file_threshold",
                                       type=int,
                                       required=True,
                                       help="Age of files to be altered when disk is critical")
    create_command_parser.add_argument("--email_usage_warnings",
                                       dest="email_usage_warnings",
                                       action="store_true",
                                       help="Send emails to users when disk is over threshold")
    create_command_parser.add_argument("--email_data_alterations",
                                       dest="email_data_alterations",
                                       action="store_true",
                                       help="Send emails when users data has been altered")
    create_command_parser.add_argument("--email_top_percent",
                                       dest="email_top_percent",
                                       type=int,
                                       default=25,
                                       help="Percent of users to flag as top users")
    create_command_parser.add_argument("--disabled",
                                       action="store_true",
                                       help="Use this flag to disable the task you are creating")

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(which="list")

    display_parser = subparsers.add_parser("display")
    display_parser.set_defaults(which="display")
    display_parser.add_argument("dtaskname", help="Name of task to display")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.set_defaults(which="remove")
    remove_parser.add_argument("rtaskname", help="Name of task to remove")

    enable_parser = subparsers.add_parser("enable")
    enable_parser.set_defaults(which="enable")
    enable_parser.add_argument("etaskname", help="Name of task to enable")

    disable_parser = subparsers.add_parser("disable")
    disable_parser.set_defaults(which="disable")
    disable_parser.add_argument("ditaskname", help="Name of task to disable")

    edit_parser = subparsers.add_parser("edit")
    edit_parser.set_defaults(which="edit")
    edit_parser.add_argument("edtaskname", help="Name of task to edit")
    edit_parser.add_argument("column_name", help="Name of column to update")
    edit_parser.add_argument("update_value", help="Value to update column with")

    return parser.parse_args(args)


def main(args=None):
    """Commandline interface"""
    if args is None:
        args = sys.argv[1:]
    args = get_args(args)
    settings = export_settings()
    taskdb = TaskDataBase(settings["DataBase_Settings"])

    if args.which == "creation_interface":
        taskdb.store(creation_interface())
    elif args.which == "creation_command":
        taskdb.store(parse_create_command(args))
    elif args.which == "list":
        taskdb.display_tasks()
    elif args.which == "display":
        taskdb.display_task_info(args.dtaskname)
    elif args.which == "remove":
        taskdb.remove_task(args.rtaskname)
    elif args.which == "enable":
        taskdb.update_column(args.etaskname, "enabled", True)
    elif args.which == "disable":
        taskdb.update_column(args.ditaskname, "enabled", False)
    elif args.which == "edit":
        taskdb.update_column(args.edtaskname, args.column_name.lower(), args.update_value)


if __name__ == "__main__":
    main()


