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

    # Private Attributes
    __lock = Lock()
    __conf = {}
    __conf_meta = {}


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

        if name in ApplicationConfig.__conf_meta:
            by_reference = ApplicationConfig.__conf_meta[name]["by_reference"]
        else:
            by_reference = True

        if name in ApplicationConfig.__conf:
            if by_reference:
                return ApplicationConfig.__conf[name]
            else:
                return copy.deepcopy(ApplicationConfig.__conf[name])
        
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

        if not name in ApplicationConfig._conf:
            raise KeyError(f"'{name}' item  not exist")

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

