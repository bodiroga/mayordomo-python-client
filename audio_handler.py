#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import uuid
import json
import time
import wave
import base64
import pyaudio
import numpy
import struct
import mqtt_handler
import logging

logger = logging.getLogger("audio_handler")

GET_AUDIO_TOPIC = "mayordomo/tts/get_audio"
GENDER = "female"

VOLUME = 100
SPEAK_TIME = None
SPEAK_RUNNING = False


def is_speak_running():
    return SPEAK_RUNNING


def set_speak_running(state):
    global SPEAK_RUNNING
    SPEAK_RUNNING = state


def speak(text="Hi,", volume=100):

    set_speak_running(True)
    payload = json.dumps({"text": text, "volume": volume})
    __speak(payload)


def __speak(text):
    global SPEAK_TIME, VOLUME
    try:
        temp = json.loads(text)
        text = temp["text"]
        VOLUME = temp["volume"]
    except ValueError:
        pass
    logger.debug("Let's say: '{}' with volume: {}".format(text, VOLUME))
    SPEAK_TIME = time.time()
    get_audio(text)


def get_audio(text=""):
    import language_handler
    tmp_topic = "mayordomo/tts/response/{}".format(str(uuid.uuid4()))
    payload = json.dumps({"topic": tmp_topic,
                          "audio_info": {"text": text, "language": language_handler.LANGUAGE.code, "gender": GENDER}})
    mqtt_handler.subscribe(tmp_topic, get_audio_response)
    mqtt_handler.publish(GET_AUDIO_TOPIC, payload, 1)
    logger.debug("Time to publish the get_audio message: {}".format(time.time() - SPEAK_TIME))


def get_audio_response(_, __, msg):
    payload = json.loads(msg.payload)

    status = payload["status"]
    if status == 200:
        data = base64.b64decode(payload["data"])
        logger.debug("Audio message correctly received")
        play_audio(data)
    mqtt_handler.unsubscribe(msg.topic)


def play_audio(data):
    global SPEAK_TIME
    logger.debug("Total time to get the audio: {} seconds".format(time.time() - SPEAK_TIME))
    SPEAK_TIME = None
    t = time.time()

    tmp_file = "tmp.wav"
    with open(tmp_file, 'wb') as f:
        f.write(data)
    wave_data = wave.open(tmp_file, 'rb')
    os.remove(tmp_file)
    logger.debug("Time to get the wave file: {} seconds".format(time.time() - t))

    data = wave_data.readframes(wave_data.getnframes())

    t_volume = time.time()
    data = numpy.fromstring(data, numpy.int16) / 100 * VOLUME  # half amplitude
    data = struct.pack('h' * len(data), *data)
    logger.debug("Time to change the volume: {} seconds".format(time.time() - t_volume))

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wave_data.getsampwidth()),
                    channels=wave_data.getnchannels(), rate=wave_data.getframerate(), output=True)
    stream.start_stream()
    stream.write(data)
    time.sleep(0.1)
    stream.stop_stream()
    stream.close()
    p.terminate()
    logger.debug("Time to play the file: {} seconds".format(time.time() - t))
    set_speak_running(False)
