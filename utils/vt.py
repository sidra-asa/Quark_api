#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


class VT:

    def __init__(self, vt_apk_key):
        self.params = {'apikey': vt_apk_key}

    def get_report(self, file_hash):
        """
        """
        url = "https://www.virustotal.com/vtapi/v2/file/report"
        params = self.params.copy()
        params.update({'resource': file_hash})

        response = requests.get(url, params=params)

        return response.json()

    def scan_file(self, file_content, file_name=None, reanalyze=None):
        """
        """
        if reanalyze:
            url = "https://www.virustotal.com/vtapi/v2/file/rescan"
        else:
            url = "https://www.virustotal.com/vtapi/v2/file/scan"

        files = {"file": (file_name, file_content)}
        response = requests.post(url, files=files, params=params)
        if response.status_code == 200:
            response_json = response.json()
        else:
            response_json = None

        return (response.status_code, response_json)
