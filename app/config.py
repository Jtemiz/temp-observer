import os
"""
This module contains different configurations for specific
tasks
"""


class BaseConfig(object):
    TOASTR_JQUERY_VERSION = '3.6.0'
    TOASTR_PREVENT_DUPLICATES = 'true'
    TOASTR_TIMEOUT = 0
    TOASTR_EXTENDED_TIMEOUT = 0

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(12)
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevConfig(object):
    DEBUG = True
    TESTING = True
    SECRET_KEY = os.urandom(12)
    DEBUG_TB_INTERCEPT_REDIRECTS = True
