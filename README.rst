************
Disk Monitor
************

Disk Monitor (dkmonitor) is a python application that allows a system adminstrator to monitor and log disk or directory usage on a multiuser system.
Disk monitor is primarily suited for use on research severs with short term fast storage drives (scratch) that are commonly missused.

Features:
=========
- Scan a disk or directory for general usage stats as well as individual user stats
- Stores directory and user stats in a postgresql database for later analisys.
- Can to push email notifications to users who are not following the speficied usage rules.
- Can automatically move all old files to a new location
- Can automatically delete old files on a disk

Installation and Setup:
=======================

**Requirements:**

1. Python 3 
2. A postgresql database


**There are 5 steps to complete installation and setup:**

1. Install dkmonitor with pip
2. Export config and log path variables in profile
3. Setup ``postgresql`` Database
4. Setup config files
5. Set ``cron`` jobs

**Install with ``pip``:**

If you want pip to install with default configurations just run: ::

    sudo pip install dkmonitor

This does three things:

1. Installs dkmonitor and its dependcies to your current python version
2. Creates a directory called dkmonitor in /etc/ where it will generate the settings files with default settings
3. Creates a directory called dkmonitor in /var/log/ where it will store log files

If you want to specify your own config and log file locations you can use one of these two options:

1. --root-path: specifes a directory where both log and config files should be stored
2. --log-path and --conf-path: Use both of these options to configure separate locations for log and config files

example: ::
    
    sudo pip install dkmonitor --root-path="/yourpath/goes/here/"


**Exporting Config and Log path variables:**

After you have successfuly installed dkmonitor with pip you need to export the config and log file path variables.

When pip is done installing it will output the two lines you need to add to your ``profile`` or ``rc`` (``.bashrc, .zshrc``) file.

Setup ``postgresql`` database:

Run the ``create_database`` command to create your postgres database: ::
    
    create_database --username user --password <your-password> --database <database-name> host <db-hostname>

The following arguments are optional:

1. --username
2. --password
3. --database

Run ``create_database -h`` for more info

**Setup configuration files:**

Go to the location of where your config file directory was installed

1. setup ``general_settings.cfg``:
   a. Add the arguments you used to setup the database with create_db to the Database_Settings section

   b. Add a user_postfix to email settings to setup email notifications
      user_postfix will be the second half of the users email address after the @ and their user name is the first half
      Example: ::

           email address: username@gmail.com
           Unix username: username
           User postfix: gmail.com

      This setting is designed for university systems where unix usernames are the first half of the user's email address

   c. Change other default settings accordingly

2. setup task files:
   - A ``task`` file specifies the settings to monitor one disk or directory
   - You can have multiple task files to monitor more than one disk or directory
   
   a. Set ``system_host_name`` to the host name of the system you want to run it on.
      If the ``system_host_name`` is incorrect the task will not run
   
   b. Set directory_path to the directory you want to search
   c. Set other settings accordingly

**Creating New Tasks:**
Use the ``create_task`` utility to create new empty task files. Create task gives you several options on where you want the new file stored

Example: ::

    $> create_task default //creates blank task file in the directory you set to store you task files (DKM_CONF)
    
    $> create_task file_name <filename> //creates a task in the default location with the file name you specify

    $> create_task full_path </path/to/task/taskname> //creates a task file in the specifed location

**Set cron Jobs:**

There are two types of scans that dkmonitor preforms: 

1. ``full scan``. -- Recursively search through every file under the specified directory and log usage stats in the database
2. ``quick scan`` -- Checks disk use, if over warning threshold start a ``full scan`` 

It is recommended that ``quick scan`` is run hourly and ``full scan`` is run nightly.
However, any cron configuration should work

To run a scan run the command: ::

    dkmonitor full

or ::
    
    dkmonitor quick


**dkviewer:**
``dkviewer`` is a command line utility that allows you to view the gathered statistics stored in your postgresql database.
``dkviewer`` will have many more viewing options in the future.

Usage: ::

    $> dkviewer all <users/systems> // displays all current users or systems in the database

    $> dkviewer user <username> //displays information about specific user (data usage, access average)

    $> dkviewer system <systemname> //displays information about the system usage including all users on the system



   
   







