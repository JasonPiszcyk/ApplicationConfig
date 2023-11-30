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

from application_config import Config


###########################################################################
#
# Start the tests...
#
###########################################################################
def test_app_cfg():
    # def register(name=None, value=None, by_reference=True, overwrite=False,
    #              constant=False):
    
    # Make sure our variables don't exist
    assert not Config.has_item("MADE_UP_ITEM")
    assert not Config.has_item("MADE_UP_CONSTANT")

    assert Config.get("MADE_UP_ITEM") is None
    assert Config.get("MADE_UP_ITEM", "a value") == "a value"

    # Register a constant and try to overwrite it
    Config.register("MADE_UP_CONSTANT", 12, constant=True)
    with pytest.raises(TypeError):
        Config.register("MADE_UP_CONSTANT", 1)

    with pytest.raises(TypeError):
        Config.register("MADE_UP_CONSTANT", 1, overwrite=True)

    with pytest.raises(TypeError):
        Config.set("MADE_UP_CONSTANT", 1)

    assert Config.get("MADE_UP_CONSTANT") == 12
    assert Config.get("MADE_UP_CONSTANT", "a value") == 12

    # Create our variable
    Config.set("MADE_UP_ITEM", "first value")
    assert Config.has_item("MADE_UP_ITEM")
    assert Config.get("MADE_UP_ITEM", "a value") == "first value"

    # Re register the item
    with pytest.raises(KeyError):
        Config.register("MADE_UP_ITEM", "Second Value")
    
    Config.register("MADE_UP_ITEM", "Second Value", overwrite=True)
    assert Config.get("MADE_UP_ITEM", "a value") == "Second Value"

    # Change the value
    Config.set("MADE_UP_ITEM", "Third Value")
    assert Config.get("MADE_UP_ITEM", "a value") == "Third Value"

    # Delete the items
    Config.delete("MADE_UP_ITEM")
    Config.delete("MADE_UP_CONSTANT")
    assert not Config.has_item("MADE_UP_ITEM")
    assert not Config.has_item("MADE_UP_CONSTANT")


def test_env_vars():
    # Make sure we can get the home variable
    home = Config.getenv('HOME')
    assert home is not None

    # Get a non-existant env Variable
    assert not Config.env_has_item('MADE_UP_ENV_VARIABLE')
    val = Config.getenv('MADE_UP_ENV_VARIABLE')
    assert val is None
    val = Config.getenv('MADE_UP_ENV_VARIABLE', "default_value")
    assert val == "default_value"

    # Set our value
    Config.setenv('MADE_UP_ENV_VARIABLE', "new_value")
    assert Config.env_has_item('MADE_UP_ENV_VARIABLE')
    val = Config.getenv('MADE_UP_ENV_VARIABLE')
    assert val == "new_value"

    # Delete our value
    val = Config.delete_env('MADE_UP_ENV_VARIABLE')
    assert not Config.env_has_item('MADE_UP_ENV_VARIABLE')
    val = Config.getenv('MADE_UP_ENV_VARIABLE')
    assert val is None
    val = Config.getenv('MADE_UP_ENV_VARIABLE', "default_value")
    assert val == "default_value"
