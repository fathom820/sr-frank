'''
rc.py
---
This file is responsible for the implementation of the random choice solution S-RC.
'''

import os
import csv
import random
from config import CONFIG, logger

def _roll_for_chance(percent_chance):
  roll = random.uniform(0, 100)
  return roll <= percent_chance

def test():
  logger.info('Testing S-RC')
  bins = CONFIG.preprocess.bins # list of bins

  for bin_ in bins:
    bin_path = f'{CONFIG.path.data.bins}{bin_}/'
    bin_files = os.listdir(bin_path)
    bin_freq = int(bin_)

    for file_ in bin_files:
      with open(f'{bin_path}{file_}', 'r') as input_file:
        csv_reader = csv.reader(input_file)
        input_file.seek(0)
        next(csv_reader)

        bin_output_path = f'{CONFIG.path.output.rc}{bin_freq}'
        if not os.path.exists(bin_output_path):
          os.makedirs(bin_output_path)

        with open(f'{bin_output_path}/{file_}', 'w') as output_file:
          csv_writer = csv.writer(output_file)
          csv_writer.writerow(['bar', 'beat', 'note', 'chord', 'replaced', 'original_value', 'solution_estimate']) # header

          for row in csv_reader:
            wrong_note = False

            if _roll_for_chance(bin_freq):
              wrong_note = True
            
            row.append(wrong_note)
            csv_writer.writerow(row)
