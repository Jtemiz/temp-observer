import os
"""
This module contains different configurations for specific
tasks
"""


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(12)
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevConfig(object):
    DEBUG = True
    TESTING = True
    SECRET_KEY = os.urandom(12)
    DEBUG_TB_INTERCEPT_REDIRECTS = True
