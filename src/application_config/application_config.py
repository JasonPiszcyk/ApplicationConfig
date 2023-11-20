#!/usr/bin/env python3
'''
* application_config.py
*
* Copyright (c) 2023 Jason Piszcyk
*
* @author: Jason Piszcyk
* 
* Application Config Info
*
'''
from threading import Lock
import copy
import os


#
# Constants
#


###########################################################################
#
# ApplicationConfig Class
#
###########################################################################
#
# ApplicationConfig
#
class ApplicationConfig():
    ''' Shared Application Config '''
    # Attributes

    # Private Attributes
    __lock = Lock()
    __lock_env = Lock()
    __conf = {}
    __conf_meta = {}


    #
    # __init__
    #
    def __init__(self, *args, **kwargs):
        ''' Init method for class '''
        super().__init__(*args, **kwargs)


    ###########################################################################
    #
    # Access methods for config data
    #
    ###########################################################################
    #
    # register
    #
    @staticmethod
    def register(name=None, value=None, by_reference=True, overwrite=False,
                 constant=False):
        '''
        Register complex data types to identify how to handle them

        Parameters:
            name: Name of the config item
            value: The config item value
            by_reference: Store a reference to the object or a deep copy
            overwrite: Allow overwrite of existing config item
            constant: Can the value be overwritten?

        Return Value:
            The config item value
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in ApplicationConfig.__conf and not overwrite:
            raise KeyError(f"'{name}' already exists")

        ApplicationConfig.__lock.acquire()
    
        ApplicationConfig.__conf[name] = {}
        ApplicationConfig.__conf_meta[name] = {}

        ApplicationConfig.__conf_meta[name]["by_reference"] = by_reference
        ApplicationConfig.__conf_meta[name]["constant"] = constant

        if by_reference:
            ApplicationConfig.__conf[name] = value
        else:
            ApplicationConfig.__conf[name] = copy.deepcopy(value)

        ApplicationConfig.__lock.release()


    #
    # get
    #
    @staticmethod
    def get(name=None, default=None):
        '''
        Get a config item

        Parameters:
            name: Name of the config item
            default: The default value to use if the item doesn't exist

        Return Value:
            The config item value
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in ApplicationConfig.__conf_meta:
            by_reference = ApplicationConfig.__conf_meta[name]["by_reference"]
        else:
            by_reference = True

        # Is it a name in our Config?
        if name in ApplicationConfig.__conf:
            if by_reference:
                return ApplicationConfig.__conf[name]
            else:
                return copy.deepcopy(ApplicationConfig.__conf[name])
        
        return default


    #
    # set
    #
    @staticmethod
    def set(name=None, value=None):
        '''
        Set a config item
        Note - Complex data types are copied by reference
        User the 'register' method to make a copy of objects

        Parameters:
            name: Name of the config item
            value: The config item value

        Return Value:
            None
        '''
        by_reference = True
 
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in ApplicationConfig.__conf_meta:
            by_reference = ApplicationConfig.__conf_meta[name]["by_reference"]
            if ApplicationConfig.__conf_meta[name]["constant"]:
                raise TypeError(f"'{name}' is defined as a constant")
    
        ApplicationConfig.__lock.acquire()

        if by_reference:
            ApplicationConfig.__conf[name] = value
        else:
            ApplicationConfig.__conf[name] = copy.deepcopy(value)

        ApplicationConfig.__lock.release()


    #
    # delete
    #
    @staticmethod
    def delete(name=None):
        '''
        Delete an item

        Parameters:
            name: Name of the config item to be deleted

        Return Value:
            None
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if not name in ApplicationConfig.__conf:
            raise KeyError(f"'{name}' item does not exist")

        # Delete the item
        ApplicationConfig.__lock.acquire()

        del ApplicationConfig.__conf[name]
        if name in ApplicationConfig.__conf_meta:
            del ApplicationConfig.__conf_meta[name]

        ApplicationConfig.__lock.release()


    #
    # has_item
    #
    @staticmethod
    def has_item(name=None):
        '''
        Determine if an item exists

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True if exists exists, False otherwise
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in ApplicationConfig.__conf:
            return True
        
        return False


    ###########################################################################
    #
    # Access methods for Environment Variables
    #
    ###########################################################################
    #
    # getenv
    #
    @staticmethod
    def getenv(name=None, default=None):
        '''
        Get an environment variable

        Parameters:
            name: Name of the environment variable
            default: The default value to use if the item doesn't exist

        Return Value:
            The environment variable value or None
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        return os.getenv(name, default=default)


    #
    # set
    #
    @staticmethod
    def setenv(name=None, value=None):
        '''
        Set an environment variable

        Parameters:
            name: Name of the environment variable
            value: The environment variable value

        Return Value:
            None
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if not value:
            raise ValueError("'value' argument must be supplied")

        ApplicationConfig.__lock_env.acquire()
        os.environ[name] = value
        ApplicationConfig.__lock_env.release()


    #
    # delete
    #
    @staticmethod
    def delete_env(name=None):
        '''
        Delete an environment variable

        Parameters:
            name: Name of the environment variable to be deleted

        Return Value:
            None
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if not name in os.environ:
            raise KeyError(f"'{name}' environment variable does not exist")

        # Delete the item
        ApplicationConfig.__lock_env.acquire()
        del os.environ[name]
        ApplicationConfig.__lock_env.release()


    #
    # env_has_item
    #
    @staticmethod
    def env_has_item(name=None):
        '''
        Determine if an environment variable exists

        Parameters:
            name: Name of the environment variable

        Return Value:
            Boolean: True if exists exists, False otherwise
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in os.environ:
            return True
        
        return False


###########################################################################
#
# Define the instance - Can be imported wherever needed:
#   from application_config import Config
#
###########################################################################
Config = ApplicationConfig()


###########################################################################
#
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass

