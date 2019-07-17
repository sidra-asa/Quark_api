#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from celery.bin import worker

from tasks.tasks import task_app

if __name__ == '__main__':
    cache_worker = worker.worker(app=task_app)

    options = {'loglevel': 'INFO', 'beat': True}

    cache_worker.run(**options)
