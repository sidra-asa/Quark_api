#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from flask import current_app
from datetime import time, datetime, timedelta
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient, HASHED, IndexModel, ASCENDING, DESCENDING


class DB(object):

    expected_fields = {'id'}

    def __init__(self):
        config = current_app.global_config
        db_server = config.get('db').get('server')
        db_port = config.get('db').get('port')
        db_name = config.get('db').get('db')
        try:
            conn = MongoClient(host=db_server, port=int(db_port))
        except:
            logging.error("DB connect error!")
            sys.exit('"DB connect error!"')
        finally:
            logging.debug("Using DB server: {0}, DB: {1}".format(db_server,
                                                                 db_name))
            self.db = conn[db_name]

        self.ensure_index()

    @classmethod
    def _clean_query(cls, origin_queries):
        """Filter unexpect fields from queries."""
        queries = origin_queries.copy()
        for key in queries.keys():
            if key not in cls.expected_fields:
                logging.debug("Drop query item: {0}".format(key))
                del queries[key]

        return queries

    def _datetime_handler(self, date):
        """Convert date to dictionary, using for querying.

        Args:
            date: query date, list type or srting type

        Returns:
            A list with two datetime object.
            example:
                {"$gte": datetime.datetime(2017, 1, 17, 15, 6, 52, 596081),
                "$lt": datetime.datetime(2017, 1, 18, 15, 6, 52, 596081)}
        """
        for_query = {}
        if isinstance(date, list):
            try:
                start_date = datetime.strptime(date[0], "%Y-%m-%d")
                end_date = datetime.strptime(date[1], "%Y-%m-%d")
            except ValueError:
                logging.error('Error in time string: {}.'.format(date))
                return None

        else:
            try:
                start_date = datetime.strptime(date, "%Y-%m-%d")
                end_date = start_date+timedelta(days=1)
            except ValueError:
                logging.error('Error in time string: {}.'.format(date))
                return None

        for_query = {"$gte": start_date, "$lt": end_date}
        logging.debug("{}".format(for_query))

        return for_query

    def ensure_index(self):
        pass

    @property
    def collection(self):
        """Shortcut for getting the appropriate collection object
        """
        cls = self.__class__
        return self.db[cls.__name__]

    def get(self, origin_queries):
        """Get rows from collection.

        Args:
            queries: query dict.
        """
        if isinstance(origin_queries, dict):
            # Using find
            logging.debug('Using find in mongo.')
            limit = origin_queries.get('limit', 0)
            queries = self.__class__._clean_query(origin_queries)
            if 'submit_date' in queries:
                queries['submit_date'] = self._datetime_handler(queries['submit_date'])
                if not queries['submit_date']:
                    return None
            elif 'publish_date' in queries:
                queries['publish_date'] = self._datetime_handler(queries['publish_date'])
                if not queries['publish_date']:
                    return None

            logging.debug("queries in {}: {}".format(__name__, queries))
            if limit == 1:
                result = self.collection.find_one(queries)
            else:
                result = self.collection.find(queries, limit=limit)

        return result

    def write(self, origin_queries):
        pass

    def delete(self, origin_queries):
        queries = self.__class__._clean_query(origin_queries)
        self.collection.remove(queries)


class apk(DB):
    expected_fields = (
        '_id',
        'source',
        'submit_date',  # date of APK submit to DB
        'name',
        'version',
        'size',
        'requirements',
        'pgname',
        'publish_date',  # date of APK publish
        'apkdata',
        'title',
        'sub_title',
        'rank',
        'sha1',
        'crc32',
        'ssdeep',
        'sha256',
        'sha512',
        'md5',
        'vt_scan',
        'av_result',
        'normal_permission',
        'danger_permission'
    )

    def ensure_index(self):
        # DNSrecord collection
        # There's Date, Client, DN, NS, and Count columns
        index1 = IndexModel([("vt_scan", ASCENDING)], background=True)
        index2 = IndexModel([("av_result", ASCENDING)], background=True)

        self.collection.create_indexes([index1, index2])
