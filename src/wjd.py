'''
wjd.py

This file is responsible for the parsing of the Weimar Jazz Database.
WJD is stored in SQLite format, which must be parsed with a proper SQL library.
Additionally, the data from this database must be converted into discrete
values that both the LSTM and RC solution can understand.
'''

# Libraries
import sqlite3

# Local
from config import CONFIG

'''
Parse the SQLite database and convert it to a file format.
'''
def parse():

  conn = sqlite3.connect(CONFIG.path.wjazzd)
  cursor = conn.cursor()

  # Execute SQL queries from cursor
  cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
  rows = cursor.fetchall()
  print(rows)

  cursor.close()
  conn.close()
