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

    # Private variables
    _lock = Lock()
    _conf = {}
    _conf_meta = {}


    #
    # __init__
    #
    def __init__(self, *arg, **kwargs):
        ''' Init method for class '''
        super().__init__(*arg, **kwargs)


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

        if name in ApplicationConfig._conf and not overwrite:
            raise KeyError(f"'{name}' already exists")

        ApplicationConfig._lock.acquire()
    
        ApplicationConfig._conf[name] = {}
        ApplicationConfig._conf_meta[name] = {}

        ApplicationConfig._conf_meta[name]["by_reference"] = by_reference
        ApplicationConfig._conf_meta[name]["constant"] = constant

        if by_reference:
            ApplicationConfig._conf[name] = value
        else:
            ApplicationConfig._conf[name] = copy.deepcopy(value)

        ApplicationConfig._lock.release()


    #
    # get
    #
    @staticmethod
    def get(name=None):
        '''
        Get a config item

        Parameters:
            name: Name of the config item

        Return Value:
            The config item value
        '''
        if not name:
            raise ValueError("'name' argument must be supplied")

        if name in ApplicationConfig._conf_meta:
            by_reference = ApplicationConfig._conf_meta[name]["by_reference"]
        else:
            by_reference = True

        if name in ApplicationConfig._conf:
            if by_reference:
                return ApplicationConfig._conf[name]
            else:
                return copy.deepcopy(ApplicationConfig._conf[name])
        
        return None


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

        if name in ApplicationConfig._conf_meta:
            by_reference = ApplicationConfig._conf_meta[name]["by_reference"]
            if ApplicationConfig._conf_meta[name]["constant"]:
                raise TypeError(f"'{name}' is defined as a constant")
    
        ApplicationConfig._lock.acquire()

        if by_reference:
            ApplicationConfig._conf[name] = value
        else:
            ApplicationConfig._conf[name] = copy.deepcopy(value)

        ApplicationConfig._lock.release()


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

        if not name in ApplicationConfig._conf:
            raise KeyError(f"'{name}' item  not exist")

        # Delete the item
        ApplicationConfig._lock.acquire()

        del ApplicationConfig._conf[name]
        if name in ApplicationConfig._conf_meta:
            del ApplicationConfig._conf_meta[name]

        ApplicationConfig._lock.release()


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

