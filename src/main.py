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
import flask

# Local
import wjd
import rc
from config import CONFIG, logger

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
`api`
---
Sending a request to root (regardless of type)
will return a debug message.
'''
@app.route('/')
def api_root():
  logger.info('api.root')
  return('Hello, I\'m the root.')

'''
`api.preprocess`
---
This API call fully pre-processes the data from csv_beats,
and generates the categories of the data needed for training and testing
S-LSTM and S-RC.

See wjd.preprocess() for more details.
'''
@app.route('/preprocess')
def api_preprocess():
  logger.info('api.preprocess')
  wjd.preprocess()
  return 'Done.'

@app.route('/test/rc')
def api_test_rc():
  logger.info('api.test.rc')
  rc.test()
  return 'Done.'
'''
SR-FRANK: BEGIN SERVER RUNTIME
'''
if __name__ == '__main__':
  logger.info(f'Starting SR-FRANK on {CONFIG.network.ip}:{CONFIG.network.port}')
  app.run(host=CONFIG.network.ip, port=CONFIG.network.port) # should be 8080 unless some idiot (me) changes it