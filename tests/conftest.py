#!/usr/bin/env python3
'''
*
* conftest.py
*
* Copyright (c) 2025 Iocane Pty Ltd
*
* @author: Jason Piszcyk
* 
* Testing Config
*
'''
import pytest
import time

from src.application_config.application_config import Config, ApplicationConfig


###########################################################################
#
# Config
#
###########################################################################
def pytest_configure(config):
    pytest.appconfig = Config

    # Set some constants we use
    pytest.EXCEPTION_MATCH_CONSTANT = "defined as a constant"
    pytest.EXCEPTION_MATCH_EXISTS = "already exists"
    pytest.EXCEPTION_MATCH_MISSING = "item does not exist"
    pytest.EXCEPTION_MATCH_MISSING_ENV = "environment variable does not exist"
    pytest.EXCEPTION_MATCH_MISSING_REDIS = "item does not exist in Redis"


###########################################################################
#
# Fixtures
#
###########################################################################
#
# redis_config
#
@pytest.fixture(scope="function")
def redis_config():
    _redis_config = ApplicationConfig(redis_host="localhost")

    return _redis_config

