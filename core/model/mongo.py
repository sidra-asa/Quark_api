#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import gridfs
import logging
from datetime import time, datetime, timedelta
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient, HASHED, IndexModel, ASCENDING, DESCENDING


class DB(object):

    expected_fields = {'id'}

    def __init__(self, db_config):
        """
        Args:
            db_config (dict): database config
        """
        config = db_config
        db_server = config.get('server')
        db_port = config.get('port')
        db_name = config.get('db')

        try:
            conn = MongoClient(host=db_server, port=int(db_port))
        except:
            logging.error("DB connect error!")
            sys.exit('"DB connect error!"')
        finally:
            logging.debug("Using DB server: {0}, DB: {1}".format(db_server,
                                                                 db_name))
            self.db = conn[db_name]
            self.fs = gridfs.GridFS(self.db)

        self.ensure_index()

    @classmethod
    def _clean_query(cls, origin_queries):
        """Filter unexpect fields from queries."""
        queries = origin_queries.copy()
        for key in origin_queries.keys():
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


class APK(DB):
    expected_fields = (
        '_id',
        'source',
        'submit_date',  # date of APK submit to DB
        'version_code',
        'version_string',
        'size',
        'permissions',
        'pgname',
        'upload_date',  # date of APK uploaded
        'apkfile',
        'apkdata',
        'title',
        'sha1',
        'crc32',
        'ssdeep',
        'sha256',
        'sha512',
        'md5',
        'vt_scan',
        'av_result'
    )

    def ensure_index(self):
        index1 = IndexModel([("vt_scan", ASCENDING)], background=True)
        index2 = IndexModel([("av_result.positives", ASCENDING)], background=True)

        self.collection.create_indexes([index1, index2])
        # self.collection.create_indexes([index1])

    def write(self, origin_queries):
        """Insert/Update row in apk collection

        Args:
            queries: query dict, or pipeline.
        """
        queries = self.__class__._clean_query(origin_queries)
        queries['submit_date'] = datetime.strptime(queries['submit_date'], "%Y-%m-%d")
        queries['upload_date'] = datetime.strptime(queries['upload_date'], "%Y-%m-%d")

        logging.debug("queries in {}: {}".format(__name__, queries))

        # Insert APK file
        if self.fs.exists({'filename': queries['sha512']}):
            logging.warn(f"{queries['pgname']} File already exists!")
            file_id = self.fs.find_one({'filename': queries['sha512']})._id
        else:
            file_id = self.fs.put(queries['apkdata'], filename=queries['sha512'])

        queries['apkfile'] = file_id

        # insert data to apk collection
        filter_obj = {
            'pgname': queries['pgname'],
            'version_code': queries['version_code'],
            'version_string': queries['version_string'],
            'title': queries['title'],
            'source': queries['source']
        }

        update_dict = {'$set': {
            'submit_date': queries['submit_date'],
            'size': queries['size'],
            'permissions': queries['permissions'],
            'upload_date': queries['upload_date'],
            'apkfile': queries['apkfile'],
            'sha1': queries['sha1'],
            'crc32': queries['crc32'],
            'ssdeep': queries['ssdeep'],
            'sha256': queries['sha256'],
            'sha512': queries['sha512'],
            'md5': queries['md5'],
            'vt_scan': queries.get('vt_scan'),
            'av_result': queries.get('av_result')
        }}
        # UpdateResult object.
        result = self.collection.update_one(filter_obj,
                                            update_dict,
                                            upsert=True)
        return result

    def get_apk_file(self, file_hash):
        """
        """
        pattern_list = [
            ("md5", re.compile(r"^[a-fA-F\d]{32}$")),
            ("sha1", re.compile(r"^[a-fA-F\d]{40}$")),
            ("sha256", re.compile(r"^[a-fA-F\d]{64}$")),
            ("sha512", re.compile(r"^[a-fA-F\d]{128}$"))
        ]
        filter_dict = {"limit": 1}
        for field_name, pattern in pattern_list:
            if pattern.match(file_hash):
                filter_dict[field_name] = file_hash
                break

        if len(filter_dict) == 1:
            raise("Malformed File hash : {}".format(file_hash))
        print(filter_dict)
        apk_info = self.get(filter_dict)
        print(apk_info)
        doc_id = apk_info["apkfile"]
        file_name = "{}.apk".format(apk_info["pgname"])
        apk_file = self.fs.get(doc_id).read()
        return (file_name, apk_file)
