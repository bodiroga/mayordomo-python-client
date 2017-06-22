#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import paho.mqtt.client as mqtt_client

logger = logging.getLogger("mqtt_handler")

CLIENT = None


def initialize(host="localhost", port=1883, username="", password="", keepalive=60):
    global CLIENT
    if CLIENT:
        stop()
    CLIENT = mqtt_client.Client("mayordomo_client")
    CLIENT.username_pw_set(username, password)
    CLIENT.on_message = on_message
    CLIENT.connect(host, port, keepalive)
    logger.debug("Client succesfully initialized")


def start():
    CLIENT.subscribe("mayordomo/#")
    logger.debug("Starting client...")
    CLIENT.loop_start()


def stop():
    CLIENT.loop_stop(True)
    logger.debug("Stopping client...")


def subscribe(topic, callback):
    CLIENT.message_callback_add(topic, callback)


def unsubscribe(topic):
    CLIENT.unsubscribe(topic)


def publish(topic, message, qos=0, retain=False):
    CLIENT.publish(topic, message, qos, retain)


def on_message(mosq, obj, msg):
    pass
