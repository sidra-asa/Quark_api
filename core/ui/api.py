#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from functools import wraps
from flask import Blueprint, request, jsonify, abort, g, current_app

from tasks.tasks import get_detail
from core.model.mongo import apk
from utils.Googleplay_api.googleplay import GooglePlayAPI, LoginError, SecurityCheckError
from conf.gplay_api_conf import LOCALE, TIMEZONE, GOOGLE_PASSWORD, GOOGLE_LOGIN

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
    gplay_api = GooglePlayAPI(LOCALE, TIMEZONE)
    try:
        gplay_api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD)
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
    db_result = apk().get({'pgname': apk_name})
    if db_result.count() == 0:
        gplay_api = initialize_login()
        permissions = getDetailsByPackName(gplay_api, apk_name).get('permission')

        return jsonify(permissions)
