#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import mqtt_handler
import pycountry
import configuration_handler
from google_cloud_speech import google_cloud_speech_handler

logger = logging.getLogger("language_handler")


class Language(object):

    def __init__(self, identifier):
        if "-" not in identifier:
            raise ValueError
        try:
            language_code = identifier.split("-")[0]
            if len(language_code) == 2:
                self.language = pycountry.languages.get(alpha_2=language_code).alpha_2
            elif len(language_code) == 3:
                self.language = pycountry.languages.get(alpha_3=language_code).alpha_2
            else:
                raise ValueError
        except:
            raise ValueError

        try:
            region_code = identifier.split("-")[1]
            if len(region_code) == 2:
                self.region = pycountry.countries.get(alpha_2=region_code).alpha_2
            elif len(region_code) == 3:
                self.region = pycountry.countries.get(alpha_3=region_code).alpha_3
            else:
                raise ValueError
        except:
            raise ValueError

        self.code = "{}-{}".format(self.language, self.region)

    def to_json(self):
        return json.dumps({"code": self.code, "language": self.language, "region": self.region})


DEFAULT_LANGUAGE = "en-US"
LANGUAGE = None
LANGUAGE_TOPIC = "/".join([configuration_handler.get_section("main")["prefix"], "configuration/language"])


def get_language():
    return LANGUAGE


def set_language(new_language):
    global LANGUAGE
    if new_language == LANGUAGE.code:
        logger.debug("Language '{}' is already in use".format(new_language))
        return
    try:
        LANGUAGE = Language(new_language)
        configuration_handler.update_configuration("language", "language_code", '{}'.format(LANGUAGE.code))
        google_cloud_speech_handler.initialize(LANGUAGE.code)
        logger.info("System language correctly changed to '{}'".format(LANGUAGE.code))
    except ValueError:
        logger.error("The language identifier '{}' is not valid".format(new_language))


def handle_message(_, __, msg):
    global LANGUAGE
    logger.debug("TOPIC: {}; MESSAGE: {}".format(msg.topic, msg.payload))
    try:
        lang = json.loads(msg.payload)["code"]
        set_language(lang)
    except KeyError:
        logger.error("Incorrect language set message: '{}'".format(msg.payload))


def initialize(language=None):
    global LANGUAGE
    if language is None:
        LANGUAGE = Language(DEFAULT_LANGUAGE)
    else:
        try:
            LANGUAGE = Language(language)
        except ValueError:
            LANGUAGE = Language(DEFAULT_LANGUAGE)
    mqtt_handler.subscribe(LANGUAGE_TOPIC, handle_message)
    logger.debug(LANGUAGE_TOPIC)
