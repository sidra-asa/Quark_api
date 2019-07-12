#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from configparser import ConfigParser


class Config(object):
    """Configuration file parser.
    """

    def __init__(self, path=os.getcwd()+'/conf'):
        """
        @param path: file path of config file.
        """
        config_list = ['db', 'celery', 'gplay_api']
        config = ConfigParser()

        for mod in config_list:
            full_filename = os.path.join(path, mod+'.conf')
            # check if config file exists
            if os.path.exists(full_filename):
                config.read(os.path.join(path, mod+'.conf'))
            else:
                logging.critical('No such config file: {}'.format(full_filename))
                sys.exit("Please add config file: {}".format(full_filename))

            self.__dict__[mod] = {}
            for name, value in config.items(mod):
                self.__dict__[mod][name] = value

    def get(self, mod):
        """Get option.
        @param mod: module config to fetch.
        @return: option value.
        """
        return getattr(self, mod)
