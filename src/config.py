'''
config.py
---
This file is responsible for the indexing and storage
of the configuration variables stored in cfg/config.yml.
'''

# Libraries

import yaml

# Converts a nested dict into a nested object
class NestedObject:
  def __init__(self, dictionary):
    for key, val in dictionary.items():
      if isinstance(val, dict):
        setattr(self, key, NestedObject(val))
      else:
        setattr(self, key, val)

'''
The config file is opened, and a custom class
is created in order to represent the configuration
as a set of nested objects.

By default, it would be stored as nested dictionaries,
and the syntax for indexing them is very annoying.
'''
with open('../cfg/config.yml', 'r') as config_file:
  config_dict = yaml.safe_load(config_file)

CONFIG = NestedObject(config_dict)