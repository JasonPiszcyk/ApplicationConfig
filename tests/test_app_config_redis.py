#!/usr/bin/env python3
'''
* test_app_config_redis.py
*
* Copyright (c) 2023 Iocane Pty Ltd
*
* @author: Jason Piszcyk
* 
* Tests for the application config class - Redis
*
'''
import pytest

###########################################################################
#
# The tests...
#
###########################################################################
#
# Status
#
class TestAppConfigRedis():
    #
    # Tests to perform on a redis based variable
    #
    def _redis_register(self, redis_config, name=""):
        _initial_value = "initial_registration_value"
        # _initial_value = 0

        # Register the variable
        redis_config.register(name=name, value=_initial_value, backing_store="redis")

        # Check to make sure it is set
        self._redis_get(redis_config, name=name, value=_initial_value)


    def _redis_check_reg(self, redis_config, name=""):
        _conf_meta = redis_config.get_registration(name=name)
        assert _conf_meta
        assert _conf_meta.backing_store == "redis"


    def _redis_set(self, redis_config, name="", value=None):
        assert name
        _default_value = "__default_value_set_by_redis_set__"

        # Make sure the variable is registered and the backing store is set to redis
        self._redis_check_reg(redis_config, name=name)

        # Set the redis variable value
        redis_config.set(name=name, value=value)

        # Do a get to make sure it is ok
        self._redis_get(redis_config, name=name, value=value, default_value=_default_value)


    def _redis_get(self, redis_config, name="", value=None, default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_redis_get__"

        # Make sure the variable is registered and the backing store is set to redis
        self._redis_check_reg(redis_config, name=name)

        # Check it exists
        assert redis_config.has_item(name=name)

        # Get the value with a default and make sure we get the value we set
        assert redis_config.get(name=name, default=default_value) == value

        # Get the value without a default and make sure we get the value we set
        assert redis_config.get(name=name) == value


    def _redis_missing_get(self, redis_config, name="", default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_redis_missing_set__"

        _conf_meta = redis_config.get_registration(name=name)
        assert not _conf_meta

        # Check if it exists
        assert not redis_config.has_item(name=name)

        # Get the value with a default and make sure we get the default
        assert redis_config.get(name=name, default=default_value) == default_value

        # Get the value without a default and make sure we get None
        assert not redis_config.get(name=name)


    def _redis_delete(self, redis_config, name=""):
        assert name
        _default_value = "__default_value_set_by_redis_delete__"

        # Make sure the variable is registered and the backing store is set to redis
        self._redis_check_reg(redis_config, name=name)

        # Delete the Item
        redis_config.delete(name=name)

        # Check the environment variable has gone
        self._redis_missing_get(redis_config, name=name, default_value=_default_value)


    #
    # Redis Values
    #
    def test_basic_redis_variable(self, redis_config):
        _var_name = "redis_var"
        _var_value = "redis_string"
        _var_default = "redis_string"

        # Make sure the value doesn't exist
        assert not redis_config.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._redis_missing_get(redis_config, name=_var_name, default_value=_var_default)

        # Register the variable
        self._redis_register(redis_config, name=_var_name)

        # Set the value (will also get the value to confirm)
        self._redis_set(redis_config, name=_var_name, value=_var_value)

        # Delete the Item
        self._redis_delete(redis_config, name=_var_name)
