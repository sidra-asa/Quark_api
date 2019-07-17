#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, abort, g, current_app

from tasks.tasks import download_apk
from core.model.mongo import APK
from utils.gplay import Gplay_API
from utils.utils import locale_timestring
# from utils.Googleplay_api.googleplay import GooglePlayAPI, LoginError, SecurityCheckError

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


def get_db_config(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        db_config = current_app.global_config.get('db')
        kwargs['db_config'] = db_config
        return func(*args, **kwargs)

    return decorated_func


@api.route('/', methods=['POST'])
@require_apikey
@get_db_config
def android_info(*args, **kwargs):
    db_config = kwargs.get('db_config')
    apk_name = request.form.get('apk_name')
    version_code = request.form.get('version_code')

    db_result = APK(db_config).get({'pgname': apk_name})
    if db_result.count() == 0:
        config = current_app.global_config
        timezone = config.get('gplay_api').get('timezone')
        locale = config.get('gplay_api').get('locale')
        account = config.get('gplay_api').get('google_login')
        password = config.get('gplay_api').get('google_password')
        gplay_api = Gplay_API(locale, timezone, account, password)
        info = gplay_api.getDetailsByPackName(apk_name)
        permissions = info.get('permission')

        return jsonify(permissions)


@api.route('/dw', methods=['POST'])
@require_apikey
def download_android(*args, **kwargs):
    apk_name = request.form.get('apk_name')
    version_code = request.form.get('version_code')
    print(apk_name, version_code)
    job_id = download_apk.apply_async(args=[apk_name, version_code])

    return jsonify(str(job_id))
