#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from celery import Celery

from utils.config import Config

config = Config()
backend_site = broker_site = config.get('celery').get('site')

task_app = Celery('Quark_API',
                  backend=backend_site,
                  broker=broker_site)

task_app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=604800 # result in backend expires after 7 days
)

if __name__ == '__main__':
    task_app.start()
