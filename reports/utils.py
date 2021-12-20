# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from datetime import datetime
from threading import Lock
import collections


def convert_to_datetime(param_value):
    if param_value == "" or param_value == "-":
        return "-"

    return datetime.strptime(
        param_value.replace("T", " ").replace("+00:00", ""),
        "%Y-%m-%d %H:%M:%S",
    )


def today_str():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')


def get_basic_value(base, value):
    if base and value in base:
        return base[value]
    return '-'


def get_value(base, prop, value):
    if prop in base:
        return get_basic_value(base[prop], value)
    return '-'


class Progress:
    def __init__(self, callback, total):
        self.lock = Lock()
        self.current = 0
        self.total = total
        self.callback = callback

    def increment(self):
        self.lock.acquire()
        self.current += 1
        self.callback(self.current, self.total)
        self.lock.release()


def get_dict_element(dictionary, *keys):
    if not keys or keys[0] not in dictionary:
        if not dictionary or isinstance(dictionary, collections.abc.Mapping):
            return ''
        return dictionary
    key = keys[0]
    return get_dict_element(dictionary[key], *keys[1:])
