#!/usr/bin/env python3
'''
* test_app_config.py
*
* Copyright (c) 2023 Iocane Pty Ltd
*
* @author: Jason Piszcyk
* 
* Tests for the application config class
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
class TestAppConfig():
    #
    # Basic Tests to perform on an item
    #
    def _item_set(self, name="", value=None):
        assert name
        _default_value = "__default_value_set_by_item_set__"

        # Set the item value
        pytest.appconfig.set(name=name, value=value)

        # Do a get to make sure it is ok
        self._item_get(name=name, value=value, default_value=_default_value)


    def _item_get(self, name="", value=None, default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_item_get__"

        # Check it exists
        assert pytest.appconfig.has_item(name=name)

        # Get the value with a default and make sure we get the value we set
        assert pytest.appconfig.get(name=name, default=default_value) == value

        # Get the value without a default and make sure we get the value we set
        assert pytest.appconfig.get(name=name) == value


    def _item_missing_get(self, name="", default_value=None):
        assert name
        if not default_value: default_value = "__default_value_set_by_item_missing_set__"

        # Check if it exists
        assert not pytest.appconfig.has_item(name=name)

        # Get the value with a default and make sure we get the default
        assert pytest.appconfig.get(name=name, default=default_value) == default_value

        # Get the value without a default and make sure we get None
        assert not pytest.appconfig.get(name=name)


    def _item_delete(self, name=""):
        assert name
        _default_value = "__default_value_set_by_item_delete__"

        # Delete the Item
        pytest.appconfig.delete(name=name)

        # Check the item has gone
        self._item_missing_get(name=name, default_value=_default_value)


    #
    # Basic config items
    #
    def test_basic_config_item(self):
        _var_name = "basic_var"
        _var_value = "basic_string"
        _var_default = "default_basic_string"

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Set the value (will also get the value to confirm)
        self._item_set(name=_var_name, value=_var_value)

        # Delete the Item
        self._item_delete(name=_var_name)


    #
    # Registered Items (Locally stored)
    #
    def test_local_registered_item(self):
        _var_name = "registered_var"
        _var_value = "registered_string"
        _var_new_value = "registered_string_new_value"
        _var_default = "default_registered_string"

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_value, by_reference=True,
                overwrite=False, constant=False, backing_store="local")

        # Check the value
        self._item_get(name=_var_name, value=_var_value, default_value=_var_default)

        # Change the value
        self._item_set(name=_var_name, value=_var_new_value)

        # Check the value has been changed
        self._item_get(name=_var_name, value=_var_new_value, default_value=_var_default)

        # Delete the Item
        self._item_delete(name=_var_name)


    def test_local_registered_item_twice(self):
        _var_name = "duplicate_registered_var"
        _var_value = "duplicate_registered_string"
        _var_default = "duplicate_default_registered_string"

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_value, by_reference=True,
                overwrite=False, constant=False, backing_store="local")

        # Check the value
        self._item_get(name=_var_name, value=_var_value, default_value=_var_default)

        # Try to register the item again
        with pytest.raises(KeyError, match=pytest.EXCEPTION_MATCH_EXISTS):
            pytest.appconfig.register(name=_var_name, value=_var_value, by_reference=True,
                    overwrite=False, constant=False, backing_store="local")

        # Delete the Item
        self._item_delete(name=_var_name)


    def test_local_registered_item_overwrite(self):
        _var_name = "overwrite_registered_var"
        _var_value = "overwrite_registered_string"
        _var_new_value = "overwrite_registered_string_new_value"
        _var_default = "overwrite_default_registered_string"

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_value, by_reference=True,
                overwrite=False, constant=False, backing_store="local")

        # Check the value
        self._item_get(name=_var_name, value=_var_value, default_value=_var_default)

        # Try to register the item again - Should work as overwrite = true
        pytest.appconfig.register(name=_var_name, value=_var_new_value, by_reference=True,
                overwrite=True, constant=False, backing_store="local")

        # Check the new value
        self._item_get(name=_var_name, value=_var_new_value, default_value=_var_default)

        # Delete the Item
        self._item_delete(name=_var_name)


    def test_local_registered_constant(self):
        _var_name = "registered_constant"
        _var_value = "registered_constant_string"
        _var_new_value = "registered_constant_string_new_value"
        _var_default = "default_registered_constant_string"

        # Make sure the constant doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_value, by_reference=True,
                overwrite=False, constant=True, backing_store="local")

        # Check the value
        self._item_get(name=_var_name, value=_var_value, default_value=_var_default)

        # Change the value
        with pytest.raises(TypeError, match=pytest.EXCEPTION_MATCH_CONSTANT):
            self._item_set(name=_var_name, value=_var_new_value)

        # Check the value has NOT been changed
        self._item_get(name=_var_name, value=_var_value, default_value=_var_default)

        # Delete the Item
        self._item_delete(name=_var_name)



    def test_local_registered_item_byref_true(self):
        _var_name = "byref_true_registered_var"
        _var_value = "byref_true_registered_string"
        _var_new_value = "byref_true_registered_string_new_value"
        _var_default = "byref_true_default_registered_string"

        _var_dict = { "value": _var_value }

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_dict, by_reference=True,
                overwrite=False, constant=False, backing_store="local")

        # Check the value
        _val = pytest.appconfig.get(name=_var_name)
        assert _val
        assert "value" in _val
        assert _val['value'] == _var_value

        # Change the value in the local variable (should be stored as a reference)
        _var_dict["value"] = _var_new_value

        # Check the value has been changed
        _val = pytest.appconfig.get(name=_var_name)
        assert _val
        assert "value" in _val
        assert _val['value'] == _var_new_value

        # Delete the Item
        self._item_delete(name=_var_name)


    def test_local_registered_item_byref_false(self):
        _var_name = "byref_false_registered_var"
        _var_value = "byref_false_registered_string"
        _var_new_value = "byref_false_registered_string_new_value"
        _var_default = "byref_false_default_registered_string"

        _var_dict = { "value": _var_value }

        # Make sure the value doesn't exist
        assert not pytest.appconfig.has_item(_var_name)

        # Try to get the value (checking that we get the default)
        self._item_missing_get(name=_var_name, default_value=_var_default)

        # Register the value
        pytest.appconfig.register(name=_var_name, value=_var_dict, by_reference=False,
                overwrite=False, constant=False, backing_store="local")

        # Check the value
        _val = pytest.appconfig.get(name=_var_name)
        assert _val
        assert "value" in _val
        assert _val['value'] == _var_value

        # Change the value in the local variable (should be stored as a copy)
        _var_dict["value"] = _var_new_value

        # Check the value has NOT been changed
        _val = pytest.appconfig.get(name=_var_name)
        assert _val
        assert "value" in _val
        assert _val['value'] == _var_value

        # Delete the Item
        self._item_delete(name=_var_name)
