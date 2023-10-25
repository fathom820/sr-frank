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
import yaml

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
  '''
  Respective read/write paths for hte respective 
  '''
  pass1_input_path = os.listdir(CONFIG.path.data.csv_beats)       # Input of pass 1 (pass 2 input)

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
            bar = row[0]
            note = row[1]             
            beat = row[2]              
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
  pass2_input_path = os.listdir(CONFIG.path.data.csv_beats_pass1)
  
  for fname in pass2_input_path:
    fpath = os.path.join(CONFIG.path.data.csv_beats, fname)

    with open(fpath, 'r', newline='') as input_file:
      # Stores entirety of note data
      note_data = []

      csv_reader = csv.reader(input_file)
      next(csv_reader)

    1


  return True
