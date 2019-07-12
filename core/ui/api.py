#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from functools import wraps
from flask import Blueprint, request, jsonify, abort, g, current_app

from core.model.mongo import apk
from utils.Googleplay_api.googleplay import GooglePlayAPI, LoginError, SecurityCheckError

api = Blueprint('api', __name__)


def require_apikey(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        api_keys = current_app.api_keys

        request_key = request.headers.get('x-api-key')
        if request_key and request_key in api_keys:
            return func(*args, **kwargs)
        else:
            abort(401)
    return decorated_func


def initialize_login():
    # first login need to use account/password
    config = current_app.global_config
    timezone = config.get('gplay_api').get('timezone')
    locale = config.get('gplay_api').get('locale')
    account = config.get('gplay_api').get('google_login')
    password = config.get('gplay_api').get('google_password')

    gplay_api = GooglePlayAPI(locale, timezone)
    try:
        gplay_api.login(account, password)
    except LoginError:
        return initialize_login()

    # you can get gsfid and subtoken after login
    gsfId = gplay_api.gsfId
    authSubToken = gplay_api.authSubToken

    # use id and authSubToken to login
    gplay_api.login(None, None, gsfId, authSubToken)
    return gplay_api


def getDetailsByPackName(gplay_api, packagename):
    details = gplay_api.details(packagename)
    return details


@api.route('/', methods=['POST'])
@require_apikey
def android_info(*args, **kwargs):
    apk_name = request.form.get('apk_name')
    version_code = request.form.get('version_code')

    db_result = apk().get({'pgname': apk_name})
    if db_result.count() == 0:
        gplay_api = initialize_login()
        permissions = getDetailsByPackName(gplay_api, apk_name).get('permission')

        return jsonify(permissions)
