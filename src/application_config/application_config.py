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
from redis import Redis
from threading import Lock
import copy
import os
from datetime import datetime, timezone


#
# Constants
#


###########################################################################
#
# ConfigMetaClass Class
#
###########################################################################
class ConfigExpiryClass():
    ''' Class to define the expiry information '''
    #
    # __init__
    #
    def __init__(self, *args, name="", backing_store="local", **kwargs):
        '''
        Class Constructor

        Parameters:
            args: Unannamed arguments
            name: The name of the item
            backing_store: Where the variable is stored (local or redis)
            kwargs: Named arguments.

        Return Value:
            None
        '''
        # Call the parent class initiator 
        super().__init__(*args, **kwargs)

        # Set the values
        self.name = name
        self.backing_store = backing_store


###########################################################################
#
# ConfigMetaClass Class
#
###########################################################################
class ConfigMetaClass():
    ''' Class to define the meta information '''
    #
    # __init__
    #
    def __init__(self, *args, backing_store="local", by_reference=True,
                constant=False, timeout=0, **kwargs):
        '''
        Class Constructor

        Parameters:
            args: Unannamed arguments
            backing_store: Where the variable is stored (local or redis)
            by_reference: Is a copy made of the value or is stored by reference
                (if a redis value, it is always copied)
            constant: Is the item a constant (ie can't be changed)
            timeout: Number of seconds before the value is expired (0 = no expiry)
            kwargs: Named arguments.

        Return Value:
            None
        '''
        # Call the parent class initiator 
        super().__init__(*args, **kwargs)

        # Set the values
        self.backing_store = backing_store
        self.by_reference = by_reference
        self.constant = constant

        if timeout >= 0:
            self.timeout = timeout
        else:
            self.timeout = 0


###########################################################################
#
# ApplicationConfig Class
#
###########################################################################
class ApplicationConfig():
    ''' Shared Application Config '''
    # Private Class Attributes
    __lock = Lock()
    __lock_env = Lock()
    __conf = {}
    __conf_meta = {}
    __conf_expiry = {}
    __redis = None


    #
    # __init__
    #
    def __init__(self, *args, **kwargs):
        '''
        Class Constructor

        Parameters:
            args: Unannamed arguments
            kwargs: Named arguments.  Anything beginning with 'redis_' will be passed as an arg
                to connect to Redis.  This allows the connection to Redis to be fully customised.
                If 'redis_host' is set, an attempt will be made to connect to Redis, and redis will
                be used as the backing store for the ApplicationConfig Module.

        Return Value:
            None
        '''
        # Extract the args for the redis connection
        _connect_to_redis = False
        _redis_args = {}
        _new_kwargs = {}

        for _key, _value in kwargs.items():
            if _key.find("redis_") == 0:
                _new_key = _key.replace("redis_", "")
                _redis_args[_new_key] = _value

                # If we have a server specified, we can connect to redis
                if _new_key == "host": _connect_to_redis = True

            else:
                # Add this to the remaining kwargs
                _new_kwargs[_key] = _value

        # Pass the remaining arguments on to parent class initiator 
        super().__init__(*args, **_new_kwargs)

        # Connect to redis if required
        if _connect_to_redis:
            self._init_redis(**_redis_args)


    #
    # _init_redis
    #
    @classmethod
    def _init_redis(cls, **kwargs):
        '''
        Initialise the connection to Redis

        Parameters:
            kwargs: Named arguments - Passed directly to Redis

        Return Value:
            None
        '''
        # Overwrite certain values for our use
        if not "port" in kwargs: kwargs["port"] = 6379
        kwargs["decode_responses"] = True

        cls.__redis = Redis(**kwargs)

        # Try an action on redis to see if connection works
        # Should raise an exception if connection doesn't work
        cls.__redis.exists("__connection_test__")


    ###########################################################################
    #
    # Helper fucntions
    #
    ###########################################################################
    #
    # __timestamp
    #
    @staticmethod
    def __timestamp(offset=0):
        '''
        Create a timestamp (in seconds) since the epoch to now

        Parameters:
            offset: Number of seconds to offset the timestamp by

        Return Value:
            int: The number of seconds since the epoch to now, +/- offset
        '''
        assert isinstance(offset, int)

        # Get the current time
        _now = datetime.now(timezone.utc)

        # Return the timestamp
        return int(_now.timestamp()) + offset


    #
    # __item_maintenance(cls)
    #
    @classmethod
    def __item_maintenance(cls):
        '''
        Perform maintenance on items (such as expiry)

        Parameters:
            None

        Return Value:
            None
        '''
        # Process the expiry list
        _now = cls.__timestamp()
        print(f"Maintence: Timestamp = {_now}")
        for _key in sorted(cls.__conf_expiry.keys()):
            # Stop processing if the timestamps are in the future
            print(f"Maintence: Key = {_key}")
            if _now < _key: break

            if cls.__conf_expiry[_key].backing_store == "local":
                # Remove the item from the local store
                cls._delete_local(name=cls.__conf_expiry[_key].name)

            # Delete the metadata
            if cls.__conf_expiry[_key].name in cls.__conf_meta:
                del cls.__conf_meta[cls.__conf_expiry[_key].name]

            # Remove the expiry entry
            cls.__lock.acquire()
            # print(f"deleting key = {_key}")
            del cls.__conf_expiry[_key]

            cls.__lock.release()


    ###########################################################################
    #
    # Access methods for local
    #
    ###########################################################################
    #
    # _set_local
    #
    @classmethod
    def _set_local(cls, name=None, value=None, by_reference=True, timeout=0):
        '''
        Set a value locally

        Parameters:
            name: Name of the config item
            value: The config item value
            by_reference: Store a reference to the object or a deep copy
            timeout: Number of seconds before the item should be deleted (0 = never)

        Return Value:
            Boolean: True is successful, False Otherwise (exception will be raised)
        '''
        assert name
        assert timeout >= 0

        cls.__lock.acquire()

        if by_reference:
            cls.__conf[name] = value
        else:
            cls.__conf[name] = copy.deepcopy(value)

        # Set the expiry for the value
        if timeout:
            _timestamp = cls.__timestamp(offset=timeout)
            cls.__conf_expiry[_timestamp] = ConfigExpiryClass(name=name,
                    backing_store="local")

        cls.__lock.release()


    #
    # _get_redis
    #
    @classmethod
    def _get_local(cls, name=None, by_reference=True):
        '''
        Get a value from redis

        Parameters:
            name: Name of the config item
            by_reference: Store a reference to the object or a deep copy


        Return Value:
            value: The config item value (exception will be raised on error), None if not found
        '''
        assert name

        _value = None

        # Get value from the local store
        if name in cls.__conf:            
            if by_reference:
                _value = cls.__conf[name]
            else:
                _value = copy.deepcopy(cls.__conf[name])

        return _value


    #
    # _delete_local
    #
    @classmethod
    def _delete_local(cls, name=None):
        '''
        Delete a value from redis

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True is successful, False Otherwise (exception will be raised)
        '''
        assert name

        # Delete the item
        if cls._has_item_local(name=name):
            cls.__lock.acquire()
            del cls.__conf[name]
            cls.__lock.release()

        return True


    #
    # _has_item_local
    #
    @classmethod
    def _has_item_local(cls, name=None):
        '''
        Get a value in redis

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True is item exists, False Otherwise
        '''
        assert name

        if name in cls.__conf:
            return True
        
        return False


    ###########################################################################
    #
    # Access methods for Redis
    #
    ###########################################################################
    #
    # _set_redis
    #
    @classmethod
    def _set_redis(cls, name=None, value=None, timeout=0):
        '''
        Set a value in redis

        Parameters:
            name: Name of the config item
            value: The config item value
            timeout: Number of seconds before the item should be deleted (0 = never)

        Return Value:
            Boolean: True is successful, False Otherwise (exception will be raised)
        '''
        assert name
        assert timeout >= 0

        # Check the type of the value
        if isinstance(value, str):
            # String
            cls.__redis.set(name, value)

        else:
            raise TypeError(f"Variable type not supported: {type(value)}")

        # Set the expire value
        if timeout: 
            # Set variable expiry in Redis (Add 1 second to make sure Metadata expires first)
            cls.__redis.expire(name, timeout + 1)

            # Set metadata to xpire
            cls.__lock.acquire()
            _timestamp = cls.__timestamp(offset=timeout)
            cls.__conf_expiry[_timestamp] = ConfigExpiryClass(name=name,
                    backing_store="redis")
            cls.__lock.release()


    #
    # _get_redis
    #
    @classmethod
    def _get_redis(cls, name=None):
        '''
        Get a value from redis

        Parameters:
            name: Name of the config item

        Return Value:
            value: The config item value (exception will be raised on error), None if not found
        '''
        assert name

        _value = None

        # Check if the value exists
        if cls._has_item_redis(name=name):
            # Check the type of the value
            _value_type = cls.__redis.type(name)
            if _value_type == "string":
                # String
                _value = cls.__redis.get(name)

            else:
                raise TypeError(f"Redis variable type not supported: {_value_type}")

        return _value


    #
    # _delete_redis
    #
    @classmethod
    def _delete_redis(cls, name=None):
        '''
        Delete a value from redis

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True is successful, False Otherwise (exception will be raised)
        '''
        assert name
        if not cls.__redis: raise RuntimeError("Redis connection has not been configured")

        if not cls._has_item_redis(name=name):
            raise KeyError(f"'{name}' item does not exist in Redis")
        
        # 'delete' should raise an exception if there is a problem
        cls.__redis.delete(name)
        return True



    #
    # _has_item_redis
    #
    @classmethod
    def _has_item_redis(cls, name=None):
        '''
        Get a value in redis

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True is item exists, False Otherwise
        '''
        assert name
        if not cls.__redis: raise RuntimeError("Redis connection has not been configured")

        # 'exists' returns a number and our return is boolen, so be explicit
        if cls.__redis.exists(name):
            return True
        else:
            return False


    ###########################################################################
    #
    # Access methods for config data
    #
    ###########################################################################
    #
    # register
    #
    @classmethod
    def register(cls, name=None, value=None, by_reference=True, overwrite=False,
                 constant=False, timeout=0, backing_store="local"):
        '''
        Register complex data types to identify how to handle them

        Parameters:
            name: Name of the config item
            value: The config item value
            by_reference: Store a reference to the object or a deep copy
                When backing store is redis, this is ignored (always a copy)
            overwrite: Allow overwrite of existing config item if it exists
            constant: Can the value be overwritten at any time?
            backing_store: Allow the data to be store in an alternate backing store
                Valid Values: local, redis

        Return Value:
            Boolean: True is successful, False Otherwise (exception will be raised)
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        _valid_backing_stores = ( "local", "redis" )
        if backing_store not in _valid_backing_stores:
            raise ValueError(f"'backing_store' must be one of {_valid_backing_stores}")

        if name in cls.__conf_meta:
            if cls.__conf_meta[name].constant:
                raise TypeError(f"'{name}' is defined as a constant")

        if name in cls.__conf and not overwrite:
            raise KeyError(f"'{name}' already exists")

        # Variable cannot be stored by reference in Redis
        if backing_store == "redis": by_reference = False

        # Update the meta info
        cls.__lock.acquire()
        cls.__conf_meta[name] = ConfigMetaClass(backing_store=backing_store,
                by_reference=by_reference, constant=constant, timeout=timeout)
        cls.__lock.release()

        if backing_store == "redis":
            # Store tha value in Redis
            cls._set_redis(name=name, value=value, timeout=timeout)
        
        else:
            # Store the value locally
            cls._set_local(name=name, value=value, by_reference=by_reference, timeout=timeout)

        return True


    #
    # get_registration
    #
    @classmethod
    def get_registration(cls, name=None):
        '''
        Register complex data types to identify how to handle them

        Parameters:
            name: Name of the config item

        Return Value:
            ConfigMetaClass: The registration info for the variable (None if not registered)
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        if name in cls.__conf_meta:
            return cls.__conf_meta[name]
        else:
            return None


    #
    # set
    #
    @classmethod
    def set(cls, name=None, value=None):
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
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        _conf_meta = cls.get_registration(name=name)
        if _conf_meta:
            # Is this a constant?
            if _conf_meta.constant: raise TypeError(f"'{name}' is defined as a constant")

            _backing_store = _conf_meta.backing_store
            _by_reference = _conf_meta.by_reference
            _timeout = _conf_meta.timeout
        else:
            _backing_store = "local"
            _by_reference = True
            _timeout = 0

        if _backing_store == "redis":
            # Value is stored in redis
            cls._set_redis(name=name, value=value, timeout=_timeout)
        
        else:
            # Value stored in the local store
            cls._set_local(name=name, value=value, by_reference=_by_reference, timeout=_timeout)


    #
    # get
    #
    @classmethod
    def get(cls, name=None, default=None):
        '''
        Get a config item

        Parameters:
            name: Name of the config item
            default: The default value to use if the item doesn't exist

        Return Value:
            The config item value
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        _conf_meta = cls.get_registration(name=name)
        if _conf_meta:
            _backing_store = _conf_meta.backing_store
            _by_reference = _conf_meta.by_reference
        else:
            _backing_store = "local"
            _by_reference = True

        # Get the value
        if _backing_store == "redis":
            # Value is stored in redis
            _value = cls._get_redis(name=name)

        else:
            # Value is stored locally
            _value = cls._get_local(name=name, by_reference=_by_reference)
        
        # Return the defaul if value not found
        if not _value: _value = default
        return _value


    #
    # delete
    #
    @classmethod
    def delete(cls, name=None):
        '''
        Delete an item

        Parameters:
            name: Name of the config item to be deleted

        Return Value:
            None
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        _conf_meta = cls.get_registration(name=name)
        if _conf_meta:
            _backing_store = _conf_meta.backing_store
        else:
            _backing_store = "local"

        if _backing_store == "redis":
            # Value is stored in redis
            cls._delete_redis(name=name)

        else:
            cls._delete_local(name=name)

        # Delete the item meta information if it exists
        if name in cls.__conf_meta:
            cls.__lock.acquire()
            del cls.__conf_meta[name]
            cls.__lock.release()


    #
    # has_item
    #
    @classmethod
    def has_item(cls, name=None):
        '''
        Determine if an item exists

        Parameters:
            name: Name of the config item

        Return Value:
            Boolean: True if exists exists, False otherwise
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        _conf_meta = cls.get_registration(name=name)
        if _conf_meta:
            _backing_store = _conf_meta.backing_store
        else:
            _backing_store = "local"

        if _backing_store == "redis":
            # Value is stored in redis
            return cls._has_item_redis(name=name)
        
        else:
            # Value is stored locally
            return cls._has_item_local(name=name)


    ###########################################################################
    #
    # Access methods for Environment Variables
    #
    ###########################################################################
    #
    # getenv
    #
    @classmethod
    def getenv(cls, name=None, default=None):
        '''
        Get an environment variable

        Parameters:
            name: Name of the environment variable
            default: The default value to use if the item doesn't exist

        Return Value:
            The environment variable value or None
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        return os.getenv(name, default=default)


    #
    # get_env - alias for getenv
    #
    get_env = getenv

    #
    # set
    #
    @classmethod
    def setenv(cls, name=None, value=None):
        '''
        Set an environment variable

        Parameters:
            name: Name of the environment variable
            value: The environment variable value

        Return Value:
            None
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        if not value:
            raise ValueError("'value' argument must be supplied")

        cls.__lock_env.acquire()
        os.environ[name] = value
        cls.__lock_env.release()


    #
    # set_env - alias for setenv
    #
    set_env = setenv


    #
    # delete
    #
    @classmethod
    def delete_env(cls, name=None):
        '''
        Delete an environment variable

        Parameters:
            name: Name of the environment variable to be deleted

        Return Value:
            None
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

        if not name in os.environ:
            raise KeyError(f"'{name}' environment variable does not exist")

        # Delete the item
        cls.__lock_env.acquire()
        del os.environ[name]
        cls.__lock_env.release()


    #
    # env_has_item
    #
    @classmethod
    def env_has_item(cls, name=None):
        '''
        Determine if an environment variable exists

        Parameters:
            name: Name of the environment variable

        Return Value:
            Boolean: True if exists exists, False otherwise
        '''
        assert name

        # Run the item maintenance
        cls.__item_maintenance()

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

