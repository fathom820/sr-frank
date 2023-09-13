#!/bin/python3
'''
main.py

This is the main function of SR-FRANK.
The Flask web framework is used in order to
create a RESTful API in order to interact with
the program. More information can be found in the
official documentation and in `readme.md`.
'''

# Libraries
import sqlite3

# Local
import wjd
import sys
import flask

from config import CONFIG

'''
API Configuration

SR_FRANK runs as a Flask web server,
and different actions can be performed via API
requests. These requests must be sent to different
API endpoints on the server, and can either be a GET
or a PUT request.
'''

# Connect Flask server to the Python application
app = flask.Flask(__name__)

'''
API: Root

Sending a request to root (regardless of type)
will return a debug message.
'''
@app.route('/')
def api_root():
  return('Hello, I\'m the root.')


'''
BEGIN PROGRAM RUNTIME
'''

if __name__ == '__main__':
  print('test')
  app.run(CONFIG.network.port) # should be 8080 unless some doofus (me) changes it