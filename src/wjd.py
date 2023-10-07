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
PRIVATE INTERFACE
'''

'''
_is_column_blank
---
Check that a given column in a given CSV reader (csv.reader)
is not entirely blank.
'''
def _is_column_blank(csv_reader, column_index):
  next(csv_reader) # skip the header

  for row in csv_reader:
    # Column has at least one row with content
    if column_index < len(row) and row[column_index].strip():
      return False

  return True # column is blank


'''
PUBLIC INTERFACE
'''


'''
preprocess
---
This function performs all of the necessary preprocessing for the data.
  1. Ignore files without bass and/or chord annotations
  2. Introduce wrong notes into the music 
  
'''
def preprocess():
  '''
  The data from each CSV file is imported,
  and is stored in memory.
  '''
  wjd_path = os.listdir(CONFIG.path.data.csv_beats)
  wjd_data = []

  for fname in wjd_path:
    fpath = os.path.join(CONFIG.path.data.csv_beats, fname)
    fcontent = [] # stores individual rows of the file
    
    with open(fpath, 'r', newline='') as csv_file:
      csv_reader = csv.reader(csv_file)

      # next(csv_reader) # skip the header

      '''
      This block filters out songs that does not meet
      the following conditions:
      - 4/4 time signature
      - 'bass_note' column isn't empty
      - 'chord' column isn't empty

      Additionally, row-wise filters are applied.
      Anything played before the first measure of the song is cut,
      and anything beyond the last full measure is also cut.

      Such filtering is done in order to ensure that only full measures will
      be processed by S-LSTM and S-RC.
      '''
      bass_pitch_index  = 1      # index of 'bass_pitch' column
      chord_index       = 3      # index of 'chord' column
      bass_pitch_empty  = True   # 'bass_pitch' is empty
      chord_empty       = True   # 'chord' is empty

      # print(fpath)

      if not _is_column_blank(csv_reader, bass_pitch_index):
        bass_pitch_empty = False

      csv_file.seek(0) # reset cursor to beginning of file

      if not _is_column_blank(csv_reader, chord_index):
        chord_empty = False

      
      '''
      This block of code starts the modification process, 
      by introducing and tagging right/wrong notes.

      Note that I'm defining chord as a chord change.
      When I reference a chord, I'm referring to how
      long that chord plays for, and for what beats
      it applies to, not to the actual details of the
      chord itself.
      
      The wrong notes are processed as follows:
        1. Get a range of notes in the song, from lowest to highest
        2. Eliminate any major outliers
        3. For every bin:
          1. For every song:
            Create a dictionary of all notes played for each chord. <string, [int]>
            1. For every chord:
              Add the notes in the current chord to the dictionary
              1. For every note:
                1. Roll for the chance to be replaced (depends on bin)
                  1. Pick a note that is not being played in the chord, and is in the pre-determined range of notes
                  2. Replace said note with the selected 
                2. If not rolled, move on

      This has to be done with as few passes through the CSV file as possible.
      '''
      if not bass_pitch_empty and not chord_empty:
        csv_file.seek(0) # return to beginning of file
        next(csv_reader)
        
        # Create a dict <str, [int]> representing all of the chords in the song and the notes played in them.
        chord_notes = {}

        for row in csv_reader:
          if int(row[0]) >= 0:       # ignore pickup measures, for consistency
            chord = row[3]
            note = row[1]

            if chord.strip():  # 'chord' field not empty
              if chord in chord_notes:
                chord_notes[chord].append(note)

      else:
        pass
        # some kind of debug message will go here instead once I get the logger set up.

  return wjd_data
