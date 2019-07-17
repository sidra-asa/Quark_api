#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import csv
import json
import logging
import requests

from io import BytesIO
from datetime import datetime
# from flask import current_app

from . import task_app
from core.model.mongo import APK

from utils.config import Config
from utils.file_obj import File
from utils.gplay import Gplay_API
from utils.utils import locale_timestring
from utils.Googleplay_api.googleplay import GooglePlayAPI


config = Config()
timezone = config.get('gplay_api').get('timezone')
locale = config.get('gplay_api').get('locale')
account = config.get('gplay_api').get('google_login')
password = config.get('gplay_api').get('google_password')
db_config = config.get('db')


@task_app.task
def download_apk(apk_name, version_code):
    """ Get APK

    Args:
        apk_name (str): Package name
        version_code (str): version code

    """
    today = datetime.today()
    gplay_api = Gplay_API(locale, timezone, account, password)
    apk_detail = gplay_api.getDetailsByPackName(apk_name)
    apk_download = gplay_api.downloadByPackageName(apk_name, version_code)
    apk_data = bytes()
    for chunk in apk_download.get('file').get('data'):
        apk_data += chunk

    if apk_data:

        to_db = {}
        to_db['vt_scan'] = False
        to_db['submit_date'] = today.strftime("%Y-%m-%d")  # submit_date
        to_db['source'] = 'googleplay'  # source
        to_db['title'] = apk_detail.get('title')  # APK name
        to_db['pgname'] = apk_detail.get('docId')  # Packagename
        to_db['version_code'] = apk_detail.get('versionCode')  # APK version code
        to_db['version_string'] = apk_detail.get('versionString')
        to_db['permissions'] = apk_detail.get('permission')
        to_db['size'] = apk_detail.get('installationSize')  # APK size
        # Upload date
        to_db['upload_date'] = datetime.strptime(apk_detail.get('uploadDate'),
                                                 locale_timestring(locale)).strftime('%Y-%m-%d')
        # Download APK
        to_db['apkdata'] = apk_data
        to_db.update(File(apk_data).all_result)

        APK(db_config).write(to_db)

    return
