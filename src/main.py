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
API: root

Sending a request to root (regardless of type)
will return a debug message.
'''
@app.route('/')
def api_root():
  return('Hello, I\'m the root.')

'''
API: test

This is a placeholder function, used only for
development of the program. Its actions frequently
change, thus there is no definition.
'''
@app.route('/')
def api_test():
  return wjd.preprocess()

'''
BEGIN PROGRAM RUNTIME
'''
if __name__ == '__main__':
  app.run(host=CONFIG.network.ip, port=CONFIG.network.port) # should be 8080 unless some idiot (me) changes it