#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import unittest
import tempfile

from utils.file_obj import File


class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.TemporaryFile()
        self.test_file.write(b'Hello World')
        self.test_file.seek(0)
        self.test_file_data = self.test_file.read()
        self.test_file_hash = File(self.test_file_data).all_result

    def test_get_md5(self):
        expection = "b10a8db164e0754105b7a99be72e3fe5"
        assert expection == self.test_file_hash.get('md5')

    def test_get_sha1(self):
        expection = "0a4d55a8d778e5022fab701977c5d840bbc486d0"
        assert expection == self.test_file_hash.get('sha1')

    def test_get_sha256(self):
        expection = "a591a6d40bf420404a011733cfb7b190"\
                    "d62c65bf0bcda32b57b277d9ad9f146e"

        assert expection == self.test_file_hash.get('sha256')

    def test_get_sha512(self):
        expection = "2c74fd17edafd80e8447b0d46741ee24"\
                    "3b7eb74dd2149a0ab1b9246fb30382f2"\
                    "7e853d8585719e0e67cbda0daa8f5167"\
                    "1064615d645ae27acb15bfb1447f459b"

        assert expection == self.test_file_hash.get('sha512')

    def test_get_ssdeep(self):
        expection = b"3:ag:ag"
        assert expection == self.test_file_hash.get('ssdeep')

    def test_get_crc32(self):
        expection = "4A17B156"
        assert expection == self.test_file_hash.get('crc32')

    def tearDown(self):
        self.test_file.close()


if __name__ == '__main__':
    unittest.main()
