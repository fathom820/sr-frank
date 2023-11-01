'''
wjd.py
---
This file is responsible for operations performed with WJD (Weimar Jazz Database),
which is the source of S-LSTM's training/testing data, as well as S-RC's testing data.

The creators of this database were kind enough to release a CSV version,
which Python is able to work with much more easily than SQL.
I chose to use this version for obvious reasons (I'm lazy).
'''

# Libraries
import os
import csv # duh
import shutil
import yaml
import random

# Local
from config import CONFIG, logger

'''
PRIVATE INTERFACE
---
The functions in this file that are preceded with an underscore (_)
are only intended to be used within this file. Python doesn't support
explicit public/private declarations.
'''

'''
_is_column_blank
---
Check that a given column in csv_reader is not entirely blank.
'''
def _is_column_blank(csv_reader, column_index):
  next(csv_reader)      # skip the header

  for row in csv_reader:
    if column_index < len(row) and row[column_index].strip():
      return False      # column isn't blank :)

  return True           # column is blank :(

'''
_is_4_4_time
---
Check that a given song is entirely in 4/4 time.
'''
def _is_4_4_time(csv_reader):
  next(csv_reader)      # skip the header
  
  for row in csv_reader:
    time_signature = row[7]

    if time_signature.strip() and time_signature != '4/4':
      return False      # song isn't all in 4/4 :(

  return True           # song is entirely in 4/4 :)

'''
_roll_for_chance
---
Rolls for a given percent chance to return True.
'''
def _roll_for_chance(percent_chance):
  roll = random.uniform(0, 100)
  return roll <= percent_chance

'''
_get_random_excluding
---
Generate a random integer between two values,
and not from a given list of unallowed values.
This is used to introduce "wrong" notes.
'''
def _get_random_excluding(low, high, given_value, exclude_list):
  exclude_set = set(exclude_list) # sets are more efficient for exclusion checking
  # Generate a list of all possible numbers
  possible_numbers = [num for num in range(low, high + 1) if num not in exclude_set and num != given_value]

  if not possible_numbers:
      return None

  # Randomly select from the remaining numbers
  return random.choice(possible_numbers)

'''
PUBLIC INTERFACE
---
These functions are called by SRF-API.
'''

'''
preprocess
---
Okay, so this function is a doozy. Sorry about that.

This performs all of the necessary preprocessing for the data with 3 passes.
  Pass 1: Filter and crop data as needed
  Pass 2: Introduce 'wrong' notes into the music based on what's not in the chord database

Note that each of these passes actually parses each song several times. It would be possible to do this
with less parses, but I find the current structure of functions easier to read/maintain,
and the difference in processing speed (on my PC) is negligible.
'''
def preprocess():
  pass1_input_path = os.listdir(CONFIG.path.data.csv_beats)       # Input of pass 1

  chord_notes = {}                                                # Dict of notes used for playing chords; shared across all files.

  logger.info('Beginning first pass')

  '''
  PASS 1: 
  This performs all necessary filtering and cropping of the data.
  '''
  for fname in pass1_input_path:
    fpath = os.path.join(CONFIG.path.data.csv_beats, fname)
    
    with open(fpath, 'r', newline='') as input_file:
      csv_reader = csv.reader(input_file)

      '''
      This block filters out songs that does not meet
      the following conditions:
        - 'bass_note' column isn't empty
        - 'chord' column isn't empty
        - 4/4 time signature for the entire song
        '''
      bass_pitch_index  = 1      # index of 'bass_pitch' column
      chord_index       = 3      # index of 'chord' column
      
      input_file.seek(0)
      bass_pitch_empty  = _is_column_blank(csv_reader, bass_pitch_index)  # If the 'bass_pitch' column is empty, there is no bass transcription.
      input_file.seek(0)
      chord_empty       = _is_column_blank(csv_reader, chord_index)       # If the 'chord' column is empty, there are no chord annotations.
      input_file.seek(0)
      is_4_4_time       = _is_4_4_time(csv_reader)                        # The only accepted time signature is 4/4 (4 beats per bar).

      '''
      If the song meets the initial filtering criteria, proceed to 
      creating another file to represent the filtered data.
      '''
      if not bass_pitch_empty and not chord_empty and is_4_4_time:
        input_file.seek(0) # return to beginning of file
        next(csv_reader)

        '''
        Create the CSV writer and the necessary file to write to.'''
        with open(f'{CONFIG.path.data.csv_beats_pass1}{fname}', 'w') as output_file:
          csv_writer = csv.writer(output_file)
          csv_writer.writerow(['bar', 'beat', 'note', 'chord']) # header

          '''
          Row-wise filters are applied.
          Anything played before the first measure of the song is cut,
          and anything beyond the last full measure is also cut.

          Such filtering is done in order to ensure that only full measures will
          be processed during Pass 2.
          '''
          for row in csv_reader:
            bar   = row[0]
            note  = row[1]             
            beat  = row[2]              
            chord = row[3]  

            if int(row[0]) > 0:          # ignore pickup measures, for consistency
              if chord.strip():           # 'chord' field not empty
                current_chord = chord

                if chord not in chord_notes:
                  chord_notes[chord] = [] # init empty list

                if note not in chord_notes[chord]:
                  chord_notes[chord].append(note)

              else:
                chord = current_chord
            
              csv_writer.writerow([bar, beat, note, chord])

      else:
        fname_quotes = f'"{fname}"' # f-string limitations are forcing me to do this
        logger.debug(f'Discarding {fname_quotes:<50} bass_empty: {bass_pitch_empty:<5} chord_empty: {chord_empty:<5} 4/4: {is_4_4_time:<5}')

  '''
  Store the chord/note database in a file for reference.
  '''
  logger.info('Dumping chord_notes')
  with open('../data/chord_notes.yml', 'w') as chord_notes_output:
    yaml.dump(chord_notes, chord_notes_output, default_flow_style=False)

  '''
  Pass 2:
  Using the database of chords and their respective note values generated in Pass 1,
  'wrong' notes are introduced into the data at varying frequencies depending on the
  bin definitions in `config.yml`. 
  '''
  logger.info('Beginning second pass')

  if os.path.exists(CONFIG.path.data.bins):
    logger.info('Clearing bins...')
    shutil.rmtree(CONFIG.path.data.bins)

  pass2_input_path = os.listdir(CONFIG.path.data.csv_beats_pass1)
  
  logger.debug('Displaying min/max notes...')
  for fname in pass2_input_path:
    fpath = os.path.join(CONFIG.path.data.csv_beats_pass1, fname)

    '''
    Open the output of the first pass to read from.
    '''
    with open(fpath, 'r', newline='') as input_file:
      note_data = [] # stores entirety of note data

      csv_reader = csv.reader(input_file)
      next(csv_reader)

      for row in csv_reader:
        note_data.append(int(row[2]))

      note_data.sort()

      '''
      IQR (interquartile range) is used here in order to eliminate
      any major pitch outliers (super high notes or super low notes)
      that do not fit into the typical pattern. This is done because
      the range from the lowest to highest note is used in order
      to produce random notes at a realistic pitch interval for the
      key the song is in, instead of just applying a basic random 
      integer generation algorithm to the whole project.
      '''
      q1 = note_data[int(len(note_data) * 0.25)]
      q3 = note_data[int(len(note_data) * 0.75)]

      iqr = q3 - q1
      iqr_mult = int(CONFIG.preprocess.iqr_multiplier)
      lower_bound = q1 - iqr_mult * iqr
      upper_bound = q3 + iqr_mult * iqr

      '''
      The note_data variable in memory is 
      overwritten with the new filtered data.
      '''
      note_data = [value for value in note_data if lower_bound <= value <= upper_bound]

      lowest_note = min(note_data)
      highest_note = max(note_data)

      fname_quotes = f'"{fname}"'
      logger.debug(f'{fname_quotes:<50} min: {lowest_note:<5} max: {highest_note:<5}')

      '''
      This block of code introduces "wrong notes" into the music
      that fit in the range of notes used, with the outliers filtered out.
      
      This is done once for every respective bin, with the notes being introduced
      at the bin's respective frequency. These bins are defined in `config.yml`.

      Afterwards, a new data file is created in the bins.
      '''
      bins = CONFIG.preprocess.bins
      
      logger.info(f'{fname_quotes:<50} Processing bins...')
      for bin_ in bins:

        bin_path = f'{CONFIG.path.data.bins}{bin_}'
        bin_freq = int(bin_)

        if not os.path.exists(bin_path):
          os.makedirs(bin_path)

        bin_file_path = f'{bin_path}/{fname}'
        with open(bin_file_path, 'w') as output_file:
          csv_writer = csv.writer(output_file)
          csv_writer.writerow(['bar', 'beat', 'note', 'chord', 'replaced', 'original_value'])
          input_file.seek(0)
          next(input_file)
          replaced_count = 0
          total_count = 0

          for row in csv_reader:
            replaced = False
            current_note = row[2]
            current_chord = row[3]

            if _roll_for_chance(bin_freq): # chance to replace note
              current_chord_notes = []

              replaced = True

              for chord in chord_notes:
                if current_chord in chord_notes:
                  current_chord_notes = chord_notes[chord]

              new_note = _get_random_excluding(lowest_note, highest_note, (current_note), current_chord_notes)
              replaced_count += 1

            '''
            Write to output
            '''
            if replaced:
              csv_writer.writerow([row[0], row[1], new_note, current_chord, replaced, current_note])
            else:
              csv_writer.writerow([row[0], row[1], current_note,current_chord, replaced, ''])
              
            total_count += 1

        bin_accuracy = replaced_count / total_count

        logger.debug(f'Bin: {bin_:<5}Total count:{total_count:<5}Replaced count: {replaced_count:<5}Actual proportion: {bin_accuracy:<5}')
           

  return True
