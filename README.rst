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

There are 5 steps to complete installation and setup:

1. Install dkmonitor with pip
2. Export config and log path variables in profile
3. Setup ``postgresql`` Database
4. Setup config files
5. Set ``cron`` jobs

Install with ``pip``:

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


Exporting Config and Log path variables:

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

Setup configuration files:

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
   
   a. Set system_name to something unique to the specific system.
      it is recomened that you all tasks on the same system have the same system name
   
   b. Set directory_path to the directory you want to search
   c. Set other settings accordingly


   
   







