************
Disk Monitor
************

Disk Monitor (dkmonitor) is a python application that allows a system adminstrator to monitor and log disk or directory usage on a multiuser system.
Disk monitor is primarily suited for use on research severs with short term fast storage drives (scratch) that are commonly missused.

Features:
=========
- Scans a disk or directory for general usage stats as well as individual user stats
- Stores directory and user stats in a postgresql database for later analisys.
- Can view usage stats on specific users or systems via the command line
- Can to push email notifications to users who are not following the speficied usage rules
- Can automatically move all old files to a new location, mirroring the directory structure
- Can automatically delete old files on a disk
- Works accross multiple separate systems 

Installation and Setup:
=======================

**Requirements:**

1. Python 3 
2. A SQL database

**Dependencies:**

1. psycopg2
2. termcolor
3. setuptools

**There are 5 steps to complete installation and setup:**

1. Install dkmonitor with setuptools
2. Export config and log path variables in profile
3. Create Database
4. Setup config files
5. Set ``cron`` jobs

**Install with setuptools:**
To install ``dkmonitor`` with default configurations first clone the repo, then run setup.py install: ::

    $> git clone https://github.com/willpatterson/dk-monitor.git
    $> cd dk-monitor
    $> python setup.py install

This does two things:

1. Installs dkmonitor and its dependcies to your current python version
2. Creates a directory called dkmonitor in ~/.dkmonitor/ (/etc/dkmonitor and /var/log/dkmonitor if you are root) where it will save a settings file with default settings and store log files

If you want to specify your own config and log file locations you can use one of these two options:

1. --root-path: specifes a directory where both log and config files should be stored
2. --log-path and --conf-path: Use both of these options to configure separate locations for log and config files

Example: ::
    
    $> python setup.py install --root-path="/yourpath/goes/here/"


**Exporting Config and Log path variables:**
If you chose a different location to store your settings or log files you will need to export that path in your environment.

When ``dkmonitor`` is done installing it will output the two lines you need to add to your ``profile`` or ``rc`` (``.bashrc, .zshrc``) file.

**Setup postgresql database:**
Create your database with the standard method of the database type you are using. After you create the database, fill out the DataBase_Settings in the settings.cfg file.

**Setup configuration files:**
Go to the location of your ``dkmonitor's`` config directory and follow the instructions below:

In ``settings.cfg``:
1. Add the login credentails you used to setup the database with create_db to the Database_Settings section.
2. Add a user_postfix to email settings to setup email notifications
   user_postfix will be the second half of the users email address after the @ and their user name is the first half
   Example: ::

           Email address: username@gmail.com
           Unix username: username
           User postfix: gmail.com

   This setting is designed for university systems where unix usernames are the first half of the user's email address
c. Change other default settings accordingly

**Creating New Tasks:**
There are two ways you can easily create tasks without touching the sql database, both using the ``dkmonitor task`` interface.

1. Captive interface:
   The captive interface walks you through task creation one setting at a time
   to use the captive interface run: ::

    $> dkmonitor task creation_interface

2. Command:
   You can also use a command to create a task. This can be a little trickier because there are a fair amount of settings.
   For more information run: ::

    $> dkmonitor task creation_command -h

``dkmonitor task`` can also be used to display, edit, and delete tasks.

**Set cron Jobs:**
``cron`` Jobs are used to run ``dkmonitor's`` scans periodically without having dkmonitor run in the background as a deamon.

There are two types of scans that dkmonitor preforms: 

1. ``full scan``. -- Recursively search through every file under the specified directory and log usage stats in the database
2. ``quick scan`` -- Checks disk use, if over warning threshold start a ``full scan`` 

It is recommended that ``quick scan`` is run hourly and ``full scan`` is run nightly.
However, any cron configuration should work

To run a scan run the command: ::

    $> dkmonitor run full

or ::
    
    $> dkmonitor run quick

``dkmonitor`` will only perform the tasks where `'hostname`` is the same as the machine's hostname.


View Command:
=============

``dkmonitor view`` is a command line utility that allows you to view the gathered statistics stored in your database.
``dkmonitor view`` will have many more viewing options in the future.

Usage: ::

    $> dkmonitor view all <users/systems> // displays all current users or systems in the database

    $> dkmonitor view user <username> //displays information about specific user (data usage, access average)

    $> dkmonitor view system <systemname> //displays information about the system usage including all users on the system


DataBase Command:
=================

``dkmonitor database`` is a command that allows your to list, drop, and clean tables in your dkmonitor database without ever touching your database directly

For more information run: ::
    $> dkmonitor database -h 


Example Emails:
===============
These are examples of the emails that dkmonitor would send if it found usage warnings on a system. These email messages will be combined into one email if a user is flagged for multiple things in one scan. The statements enclosed in the curly braces ({}) will be replaced with the proper data at runtime.

Email sent if data might be moved: ::

    Dear {user_name},
    You have been flagged for improper use of {searched_directory} on {system}.
    Please address the message(s) below to fix the problem.

    WARNING: Disk {directory_path} on {system_host_name} is over it's warning quota of {disk_use_percent_warning_threshold} %
    If {directory_path} is over its critical threshold of {disk_use_percent_critical_threshold} % all files accessed more than {last_access_threshold} days ago will be moved to {file_relocation_path} 

    Number of old files: {number_of_old_files}
    Combined size of old files: {total_old_file_size} GBs

Email sent if data will be moved: ::

    Dear {user_name},
    You have been flagged for improper use of {searched_directory} on {system}.
    Please address the message(s) below to fix the problem.

    IMPORTANT WARNING: Disk {directory_path} on {system_host_name} is over it's critical quota of {disk_use_percent_critical_threshold} %
    All files older than {last_access_threshold} days are being moved to {file_relocation_path}

    Number of old files you own: {number_of_old_files}
    Combined size of your old files: {total_old_file_size} GBs

Email sent if user is a top consumer of diskspace: ::

    Dear {user_name},
    You have been flagged for improper use of {searched_directory} on {system}.
    Please address the message(s) below to fix the problem.

    WARNING: You have been flagged as a top space user of {searched_directory} on
    {system}.
    {searched_directory} is over it's use threshold. Please reduce your data usage.
    Total size of all files: {total_file_size} GBs
    Total disk use: {disk_use_percent} %

Email sent if user is a top holder of old data: ::

    Dear {user_name},
    You have been flagged for improper use of {searched_directory} on {system}.
    Please address the message(s) below to fix the problem.

    WARNING: You have been flagged as a top owner of old files in {searched_directory} on {system}.
    Please use or remove all of your old files or they will be removed for you.
    Average age of all your files: {last_access_average} days


