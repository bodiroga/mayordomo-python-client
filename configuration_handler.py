#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import yaml
import os

logger = logging.getLogger("configuration_handler")

CONFIGURATION_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILENAME = "configuration.yml"
FILENAME = None
CONFIG = None


def load_configuration(filename=None):
    global FILENAME, CONFIG
    if not filename:
        FILENAME = DEFAULT_FILENAME
    else:
        FILENAME = filename

    configuration_path = "/".join([CONFIGURATION_FOLDER, FILENAME])

    try:
        with open(configuration_path, 'r') as ymlfile:
            CONFIG = yaml.load(ymlfile)
            logger.debug("Configuration file '{}' loaded".format(FILENAME))
    except IOError:
        logger.error("Configuration file '{}' does not exist, exiting".format(FILENAME))
        import sys
        sys.exit(1)


def update_configuration(section, param, value):
    global CONFIG
    if not CONFIG:
        logger.error("No configuration file loaded")
        return

    CONFIG[section][param] = value

    configuration_path = "/".join([CONFIGURATION_FOLDER, FILENAME])

    try:
        with open(configuration_path, 'w') as outfile:
            yaml.dump(CONFIG, outfile, default_flow_style=False)
    except IOError:
        logger.error("Configuration file '{}' does not exist".format(FILENAME))


def get_section(section):
    if not CONFIG:
        logger.error("No configuration file loaded")
        return

    try:
        return CONFIG[section]
    except KeyError:
        logger.error("Section '{}' does not exist".format(section))
