#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import threading
import os
import time
import json
from snowboy import snowboydecoder
import google_cloud_speech_handler
import mqtt_handler
import audio_handler
import configuration_handler as config

MODEL_NAME = "mayordomo.pmdl"

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(name)-20s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("main")


class VoiceCommandHandler(object):
    def __init__(self, prefix="mayordomo", device_name="", device_location="", owner="", description=""):
        if not device_name:
            raise ValueError
        self.device_name = device_name
        self.device_location = device_location
        self.device_owner = owner
        self.device_description = description
        self.mayordomo_prefix = prefix
        self.register_topic = "{}/devices/register".format(self.mayordomo_prefix)
        self.answer_topic = "{}/devices/{}/answer".format(self.mayordomo_prefix, self.device_name)
        self.question_counter = 0
        mqtt_handler.subscribe(self.answer_topic, self.answer_handler)
        self.advertise_device()

    def advertise_device(self):
        register_topic = "{}/devices/register/{}".format(self.mayordomo_prefix, self.device_name)
        register_payload = {"name": self.device_name, "owner": self.device_owner,
                             "description": self.device_description, "location": self.device_location}
        mqtt_handler.publish(register_topic, json.dumps(register_payload), 1, True)

    def answer_handler(self, _, __, msg):
        answer = json.loads(msg.payload)
        answer_category = answer["category"]
        answer_text = answer["text"]
        if answer_category == "question":
            if self.question_counter > 2:
                audio_handler.speak("Too many retries")
                self.question_counter = 0
                return
            audio_handler.speak(answer_text)
            threading.Thread(target=self.process_question).start()
            self.question_counter += 1
        else:
            self.question_counter = 0
            audio_handler.speak(answer_text)

    def process_question(self):
        while audio_handler.is_speak_running():
            time.sleep(0.1)
        speech_recognition()

    def process_voice_command(self, topic="mayordomo/utterance/message", payload=""):
        mqtt_handler.publish(topic, payload)

    def complete_silence(self, value):
        pass


def stream_recognition():
    vch.complete_silence("ON")
    snowboydecoder.play_on_sound()
    start_time = time.time()
    message = google_cloud_speech_handler.start()
    if not message:
        snowboydecoder.play_error_sound()
        vch.complete_silence("OFF")
        return
    snowboydecoder.play_ok_sound()
    logger.info("You said: {0} ({1} seconds)".format(message, time.time() - start_time))
    payload = {"device_name": config.get_section("main")["name"], "user_name": "aitor", "message": message}
    vch.process_voice_command(payload=json.dumps(payload))


def speech_recognition():
    logger.debug("Listening to your voice...")
    threading.Thread(target=stream_recognition).start()


if __name__ == "__main__":
    config.load_configuration()

    logger.info("Starting '{}' mayordomo client".format(config.get_section("main")["name"]))

    mqtt_handler.initialize(config.get_section("mqtt")["host"], config.get_section("mqtt")["port"],
                            config.get_section("mqtt")["username"], config.get_section("mqtt")["password"])

    import language_handler
    language_handler.initialize(config.get_section("language")["language_code"])

    mqtt_handler.start()

    google_cloud_speech_handler.initialize(language_handler.get_language().code)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "voice_models/%s" % MODEL_NAME)

    vch = VoiceCommandHandler(config.get_section("main")["prefix"], config.get_section("main")["name"],
                              config.get_section("main")["location"], config.get_section("main")["owner"],
                              config.get_section("main")["description"])

    detector = snowboydecoder.HotwordDetector(model_path, sensitivity=0.4)

    snowboydecoder.play_on_sound()
    detector.start(detected_callback=speech_recognition, sleep_time=0.03)
    detector.terminate()
