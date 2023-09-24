'''
wjd.py

This file is responsible for the parsing of the Weimar Jazz Database.
WJD is stored in SQLite format, which must be parsed with a proper SQL library.
Additionally, the data from this database must be converted into discrete
values that both the LSTM and RC solution can understand.
'''

# Libraries
import os
import csv

# Local
from config import CONFIG

'''
1. Import the CSV data
'''
def preprocess():
  '''
  The data from each CSV file is imported,
  and is stored in '''
  wjd_path = os.listdir(CONFIG.path.csv_beats)
  wjd_data = []

  for fname in wjd_path:
    fpath = os.path.join(CONFIG.path.csv_beats, fname)
    fcontent = [] # stores individual rows of the file
    
    with open(fpath, 'r', newline='') as csv_file:
      csv_reader = csv.reader(csv_file)

      # next(csv_reader) # skip the header

      for row in csv_reader:
        fcontent.append(row)
        # print(fcontent)
      
      wjd_data.append(fcontent)

  return wjd_data
