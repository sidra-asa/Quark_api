#!/usr/bin/env python
# -*- coding: utf-8 -*-


def locale_timestring(locale):
    timestrings = {
        'en_US': '%b %d, %Y',
        'zh_TW': u'%Y年%m月%d日',
    }

    return timestrings.get(locale)
