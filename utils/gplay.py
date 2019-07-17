#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from utils.Googleplay_api.googleplay import GooglePlayAPI, LoginError, SecurityCheckError


class Gplay_API():
    def __init__(self, LOCALE, TIMEZONE, GOOGLE_LOGIN, GOOGLE_PASSWORD):
        # first login need to use account/password
        gplay_api = GooglePlayAPI(LOCALE, TIMEZONE)
        try:
            gplay_api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD)
        except LoginError:
            return self.__init__(LOCALE, TIMEZONE, GOOGLE_LOGIN, GOOGLE_PASSWORD)

        # you can get gsfid and subtoken after login
        gsfId = gplay_api.gsfId
        authSubToken = gplay_api.authSubToken

        # use id and authSubToken to login
        gplay_api.login(None, None, gsfId, authSubToken)
        self.gplay_api = gplay_api

    def getDetailsByPackName(self, packagename):
        details = self.gplay_api.details(packagename)
        return details

    def downloadByPackageName(self, packagename, versioncode=None):
        apk_data = self.gplay_api.download(packagename,
                                           versioncode
                                           )
        return apk_data
