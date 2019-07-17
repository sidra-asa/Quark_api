#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import hashlib
import pydeep
import logging


class File:

    """File hashes"""

    def __init__(self, data):
        self.result = {}
        self._file_data = data
        self.calc_hashes()
        logging.debug("file hashes: {0}".format(self.result))

    def calc_hashes(self):
        data = self._file_data

        crc = 0
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()

        crc = binascii.crc32(data, crc)
        md5.update(data)
        sha1.update(data)
        sha256.update(data)
        sha512.update(data)

        self.result['md5'] = md5.hexdigest()
        self.result['sha1'] = sha1.hexdigest()
        self.result['sha256'] = sha256.hexdigest()
        self.result['sha512'] = sha512.hexdigest()
        self.result['crc32'] = "".join("%02X" % ((crc >> i) & 0xff) for i in [24, 16, 8, 0])
        self.result['ssdeep'] = self._get_ssdeep()

    def _get_ssdeep(self):
        try:
            return pydeep.hash_buf(self._file_data)
        except Exception as e:
            logging.warn(f"Error: {e}")
            return None

    @property
    def all_result(self):
        return self.result
