import configparser

from configparser import NoOptionError
from configparser import NoSectionError

import sys, os
sys.path.append(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("/")] + "/")

from dkmonitor.utilities.log_setup import setup_logger

class ConfigurationFilesNotFoundError(Exception):
    def __init__(self, message):
        super(ConfigurationFilesNotFoundError, self).__init__(message)

class SettingsFileNotFoundError(Exception):
    def __init__(self, message):
        super(SettingsFileNotFoundError, self).__init__(message)

def load_settings():
    raw_settings = configparser.ConfigParser()
    file_not_found = False
    try:
        raw_settings.read("/etc/dkmonitor.cfg")
    except IOError as e:
        print("TEST")
        if (e[0] == errno.EPERM):
            print("You do not have permission to read /etc/dkmonitor.cfg", file=sys.stderr)
            file_not_found = True

    if (len(raw_settings) == 1) or (file_not_found is True):
        print("No setting file found at /etc/dkmonitor.conf, checking ~/.dkmonitor/settings.cfg", file=sys.stderr)
        raw_settings.read(os.path.expanduser("~/.dkmonitor/settings.conf"))

    if (len(raw_settings) == 1):
        print("No settings file found at ~/.dkmonitor/settings.conf, checking DKM_CONF", file=sys.stderr)
        try:
            print(os.path.join(os.environ["DKM_CONF"], "settings.cfg"))
            raw_settings.read(os.path.join(os.environ["DKM_CONF"], "settings.cfg"))
        except KeyError as e:
            raise ConfigurationFilesNotFoundError("DKM_CONF is not set, no settings file found")

    if len(raw_settings) == 1:
        raise SettingsFileNotFoundError("No settings file found at any designated locations")

    return raw_settings

def export_settings():
    raw_settings = load_settings()
    formatted_settings = {}
    for section in raw_settings.sections():
        formatted_settings[section] = section_to_dict(raw_settings, section)

    return formatted_settings

def section_to_dict(raw_settings, section):
    formatted_section = dict(raw_settings.items(section))
    for field in formatted_section.keys():
        if formatted_section[field].isdigit():
            formatted_section[field] = int(formatted_section[field])

    return formatted_section

