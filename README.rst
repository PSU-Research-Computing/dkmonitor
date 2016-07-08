.. image:: https://travis-ci.org/willpatterson/DkMonitor.svg?branch=master
    :target: https://travis-ci.org/willpatterson/DkMonitor

************
Disk Monitor
************

Disk Monitor (dkmonitor) is a python application that allows a system 
adminstrator to monitor and log disk or directory usage on a multiuser system.
Disk monitor is primarily suited for research computing systems with short-term
fast storage drives (scratch) that are commonly missused.

**DkMonitor is pre-release software, and is currently being refactored** 

Features:
=========
- Scans a disk or directory for general usage stats as well as individual user 
  stats
- Stores directory and user stats in a database (SQLite, postgres, MySQL) for 
  later analisys.
- Can view usage stats on specific users or systems via the command line
- Can to push email notifications to users who are not following the speficied 
  usage rules
- Can automatically move all old files to a new location, mirroring the 
  directory structure
- Can automatically delete old files on a disk
- Works accross multiple separate systems 

Installation and Setup:
=======================

**Requirements:**

1. Python 3 
2. A SQL database

**Dependencies:**

1. sqlalchemy
2. termcolor
3. setuptools

**There are 5 steps to complete installation and setup:**

1. Install dkmonitor with setuptools
2. Export config and log path variables in profile (if nessesary)
3. Create your database
4. Setup config files
5. Set ``cron`` jobs

**Install with setuptools:**
To install ``dkmonitor`` with default configurations first clone the repo,
then run setup.py install: ::

    $> git clone https://github.com/willpatterson/dk-monitor.git
    $> cd dk-monitor
    $> python setup.py install

This does two things:

1. Installs dkmonitor and its dependcies to your current python version
2. Creates a directory called dkmonitor in ~/.dkmonitor/ (/etc/dkmonitor and 
   /var/log/dkmonitor if you are root) where it will save a settings file with
   default settings and store log files

.. note:: ``dkmonitor`` uses ``PostgreSQL`` as the default database on 
            installation. The setup.py script will install ``psycopg2`` as the
            default interface for ``sqlalchemy``. If you plan on using a 
            different database like ``MySQL`` or ``SQLlite`` you will need to 
            install the nessary python module for ``sqlalchemy`` to interface 
            with that type of database.

**Exporting Config and Log path variables:**
If you want to specify your own config and log file locations you can use one 
of these two options you need to create you own directories for log/config 
files and specify their location(s) with the ``DKM_CONF`` (settings file) and 
``DKM_LOG`` (log files) environemnt variables in your ``rc`` or ``profile`` 
config files

``dkmonitor`` will look for these locations before looking in the default 
locations created when its installed

**Setup postgresql database:**
Create your database with the standard method of the database type you are 
using. After you create the database, fill out the DataBase_Settings in the 
settings.cfg file.

**Setup configuration files:**
Go to the location of your ``dkmonitor's`` config directory and follow the 
instructions below:

In ``settings.cfg``:

1. Add the login credentails you used to setup the database with create_db to 
   the Database_Settings section.

2. Add a user_postfix to email settings to setup email notifications. 
   user_postfix will be the second half of the users email address after the 
   @ and their user name is the first half

Example: ::

           Email address: username@gmail.com
           Unix username: username
           User postfix: gmail.com

This setting is designed for university systems where unix usernames are the 
first half of the user's email address

3. Change other default settings accordingly

**Creating New Tasks:**
There are two ways you can easily create tasks without touching the sql 
database, both using the ``dkmonitor task`` interface.

1. Captive interface:
   The captive interface walks you through task creation one setting at a time
   to use the captive interface run: ::

    $> dkmonitor task creation_interface

2. Command:
   You can also use a command to create a task. This can be a little trickier 
   because there are a fair amount of settings.
   For more information run: ::

    $> dkmonitor task creation_command -h

``dkmonitor task`` can also be used to display, edit, and delete tasks.

**Set cron Jobs:**
``cron`` Jobs are used to run ``dkmonitor's`` scans periodically without having
dkmonitor run in the background as a deamon.

There are two types of scans that dkmonitor preforms: 

1. ``full scan``. -- Recursively search through every file under the specified
   directory and log usage stats in the database
2. ``quick scan`` -- Checks disk use, if over warning threshold start a 
   ``full scan`` 

It is recommended that ``quick scan`` is run hourly and ``full scan`` is run 
nightly. However, any cron configuration should work

To run a scan routine run the command: ::

    $> dkmonitor run full

or ::
    
    $> dkmonitor run quick

``dkmonitor`` will only perform the tasks where `'hostname`` is the same as the
machine's hostname.

View Command:
=============

``dkmonitor view`` is a command line utility that allows you to view the 
gathered statistics stored in your database. ``dkmonitor view`` will have many 
more viewing options in the future.

Usage: ::

    $> dkmonitor view all <users/systems> //all current users or systems in the database

    $> dkmonitor view user <username> // information about specific users

    $> dkmonitor view system <systemname> //information about the system usage including all users on the system


DataBase Command:
=================

``dkmonitor database`` is a command that allows your to list, drop, and clean 
tables in your dkmonitor database without ever touching your database directly

For more information run: ::

    $> dkmonitor database -h 

Example Emails:
===============
These are examples of the emails that dkmonitor would send if it found usage 
warnings on a system. These email messages will be combined into one email 
if a user is flagged for multiple things in one scan. The statements enclosed 
in the curly braces ({}) will be replaced with the proper data at runtime.

**Usage Warnings:** 

Message Header: ::
    
    Dear {username},
    You have been flagged for improper use of {target_path} on {hostname}.
    Please address the message(s) below to fix the problem.

General Warning: ::

    If {target_path} is over its critical threshold of {usage_critical_threshold} % all files accessed more than {old_file_threshold} days ago will be moved to {relocation_path} 

    Your Data:
    Number of old files that will be moved: {number_of_old_files}
    Combined size of old files............: {total_old_file_size} GBs

Top Space Use: ::

    WARNING: You have been flagged as a top space user of {target_path} on {hostname}.
    {target_path} is over it's use threshold. Please reduce your data usage.
    Total size of all files: {total_file_size} GBs
    Total disk use: {disk_use_percent} %

Top Number of Old Files to Space Use: ::

    WARNING: {target_path} on {hostname} is over it's use threshold. Please reduce your data usage.

    Your Data:
    Total size of all files: {total_file_size} GBs
    Total disk use: {disk_use_percent} %


**Data Alteration Notices:**

Deletion Warning: ::

    WARNING: Disk {target_path} on {hostname} is over it's warning quota of {usage_warning_threshold} %
    When {target_path} is over it's critical threshold of {usage_critical_threshold} % all files accessed more than {old_file_threshold} days ago will be deleted.

    Your Data:
    Number of old files that will be deleted.......: {number_of_old_files}
    Combined size of old files that will be deleted: {total_old_file_size} GBs

Deletion Notice: ::

    IMPORTANT NOTICE: Disk {target_path} on {hostname} is over it's critical quota of {usage_critical_threshold} %
    All files older than {old_file_threshold} days have been moved DELETED.

    Your Data:
    Number of old files you own that were deleted: {number_of_old_files}
    Combined size of your old deleted files......: {total_old_file_size} GBs

Move Warning: ::

    If {target_path} is over its critical threshold of {usage_critical_threshold} % all files accessed more than {old_file_threshold} days ago will be moved to {relocation_path} 

    Your Data:
    Number of old files that will be moved: {number_of_old_files}
    Combined size of old files............: {total_old_file_size} GBs

Move Notice: ::

    IMPORTANT NOTICE: Disk {target_path} on {hostname} is over it's critical quota of {usage_critical_threshold} %
    All files older than {old_file_threshold} days have been moved to {relocation_path}

    Your Data:
    Number of old files you own that have been moved: {number_of_old_files}
    Combined size of your old moved files...........: {total_old_file_size} GBs

    

