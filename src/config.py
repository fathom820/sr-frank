'''
config.py
---
This file is responsible for the indexing and storage
of the configuration variables stored in cfg/config.yml.

This file is also responsible for setting up the logging
framework, which is handled via the Loguru library.
'''

# Libraries
import yaml
from loguru import logger
from datetime import datetime

'''
NestedObject
---
This class converts a set of nested dictionaries
into a nest of objects. This was done purely for
QOL when coding, as config.yml is imported by the
YAML library as nested dictionaries.

The Python syntax for nested objects looks.like.this.
The Python syntax for nested dictionaries looks['like']['this']. 

One is much more readable than the other, 
hence my design choice.
'''
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

'''
Set up the logging framework.
'''
current_date = datetime.now().strftime('%Y-%m-%d')
log_filename = f'sr-frank_{current_date}.log'
log_format = '{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {name:<10}{function:<20}{line:<3} | {message}'

logger.add(f'{CONFIG.logging.info_path}info_{log_filename}', rotation='1 day', format=log_format, level='INFO')
logger.add(f'{CONFIG.logging.debug_path}debug_{log_filename}', rotation='1 day', format=log_format, level='DEBUG')