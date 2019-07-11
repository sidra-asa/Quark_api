#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging

from flask import Flask

logging.basicConfig(level=logging.DEBUG)


def read_apikey_file():
    try:
        with open('conf/auth_key.json', 'rb') as f:
            api_keys = json.load(f)
    except FileNotFoundError:
        sys.exit("auth_key.json not found in conf!")

    return api_keys


if __name__ == '__main__':
    from core.ui.api import api

    app = Flask(__name__)
    app.api_keys = read_apikey_file()
    app.register_blueprint(api)

    app.run(host='0.0.0.0', port=8000, threaded=True)
