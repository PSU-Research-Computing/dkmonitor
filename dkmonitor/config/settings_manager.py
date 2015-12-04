"""
This module loads the settings.cfg file and parses the settings into a dict
"""

import configparser

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.log_setup import setup_logger

class SettingsFileNotFoundError(Exception):
    """Error for when settings.cfg is not found"""
    def __init__(self, message):
        super(SettingsFileNotFoundError, self).__init__(message)


logger = setup_logger(__name__)

def load_settings():
    """Loads settings.cfg into a configparser object"""
    raw_settings = configparser.ConfigParser()

    raw_settings.read("/etc/dkmonitor.cfg")
    if len(raw_settings) == 1:
        raw_settings.read(os.path.expanduser("~/.dkmonitor/settings.conf"))
    if len(raw_settings) == 1:
        try:
            raw_settings.read(os.path.join(os.environ["DKM_CONF"], "settings.cfg"))
        except KeyError:
            logger.error("No configuration files found: DKM_CONF not set")
            raise SettingsFileNotFoundError("DKM_CONF is not set, no settings file found")
    if len(raw_settings) == 1:
        logger.error("No configuration files found")
        raise SettingsFileNotFoundError("No settings file found at any designated locations")

    return raw_settings

def export_settings():
    """Exports all settings as a dictionary"""
    raw_settings = load_settings()
    formatted_settings = {}
    for section in raw_settings.sections():
        formatted_settings[section] = section_to_dict(raw_settings, section)

    return formatted_settings

def section_to_dict(raw_settings, section):
    """Converts each section of the settings file into a dictionary"""
    formatted_section = dict(raw_settings.items(section))
    for field in formatted_section.keys():
        if formatted_section[field].isdigit():
            formatted_section[field] = int(formatted_section[field])

    return formatted_section
