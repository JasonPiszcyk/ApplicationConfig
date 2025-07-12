#!/usr/bin/env python3
'''
* test_app_config_env.py
*
* Copyright (c) 2023 Iocane Pty Ltd
*
* @author: Jason Piszcyk
* 
* Tests for the application config class - Environment Variables
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
class TestAppConfigEnv():
    #
    # Basic Tests to perform on an environment variable
    #
    def _env_set(self, name="", value=None):
        assert name
        _default_value = "__default_value_set_by_env_set__"

        # Set the environment variable value
        pytest.appconfig.set_env(name=name, value=value)

        # Do a get to make sure it is ok
        self._env_get(name=name, value=value, default_value=_default_value)


    def _env_get(self, name="", value=None, default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_env_get__"

        # Check it exists
        assert pytest.appconfig.env_has_item(name=name)

        # Get the value with a default and make sure we get the value we set
        assert pytest.appconfig.get_env(name=name, default=default_value) == value

        # Get the value without a default and make sure we get the value we set
        assert pytest.appconfig.get_env(name=name) == value


    def _env_missing_get(self, name="", default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_env_missing_set__"

        # Check if it exists
        assert not pytest.appconfig.env_has_item(name=name)

        # Get the value with a default and make sure we get the default
        assert pytest.appconfig.get_env(name=name, default=default_value) == default_value

        # Get the value without a default and make sure we get None
        assert not pytest.appconfig.get_env(name=name)


    def _env_delete(self, name=""):
        assert name
        _default_value = "__default_value_set_by_env_delete__"

        # Delete the Item
        pytest.appconfig.delete_env(name=name)

        # Check the environment variable has gone
        self._env_missing_get(name=name, default_value=_default_value)


    #
    # Environment Vars
    #
    def test_env_variable_home(self):
        _var_name = "HOME"

        # Make sure the 'HOME' environment variable exists
        assert pytest.appconfig.env_has_item(_var_name)


    def test_basic_env_variable(self):
        _var_name = "environment_var"
        _var_value = "environment_string"
        _var_default = "environment_string"

        # Make sure the value doesn't exist
        assert not pytest.appconfig.env_has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._env_missing_get(name=_var_name, default_value=_var_default)

        # Set the value (will also get the value to confirm)
        self._env_set(name=_var_name, value=_var_value)

        # Delete the Item
        self._env_delete(name=_var_name)
