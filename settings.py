import os

# Directory where the main.py and setting.py scripts is located
INSTALL_DIR = os.getcwd()

os.chdir(INSTALL_DIR)
TEMP_PATH = f'{INSTALL_DIR}/temp'
os.makedirs(TEMP_PATH, exist_ok = True)

IMAGES = f'{INSTALL_DIR}/images'

# Color codes used in the program
COLORS = ['#000000', '#FF0000', '#DB7400', '#00931D', '#0050A4', 
          '#6712AD', '#D95BE5', '#918F18', '#4BB379', '#4B8CB3', 
          '#976637', '#6AB820', '#787878', '#E5E100', '#13DED8', 
          '#E3009B', '#78324C', '#937DAC', '#099F6F', '#D29051']

# Log messages dictionary
LOGS = {'open':             'Maps loaded successfully',
        'replace':          'Loaded maps deleted',
        'individual_save':  'Individual spectra saved',
        'average_save':     'Average spectra saved',
        'cut':              'Spectra were cut', 
        'cut_saveMap':      'Cut maps were saved',
        'baseline':         'Baseline subtracted', 
        'subAverage_save':  'Subtracted average spectra saved',
        'importbaseline':   'Baseline parameters imported successfully',
        'baseline_saveMap': 'Subtracted maps were saved',
        'shift':            'Shifted maps were saved', 
        'importfit':        'Band parameters imported successfully',
        'fitGuide':         'Guide spectra fitted',
        'fitMap':           'Maps were fitted' }

# Text for the About window
ABOUT_TITLE = 'Horiba LabRam Automatic\nMap Processing Software\n'

ABOUT_TEXT  = 'This software is a complement of the Horiba LabSpec6\nadquisition and processing software.\n\n' 
ABOUT_TEXT += 'Developed by Leandro Benavides in the\nRaman Biophysicalchemistry Lab at INQUIMAE, Buenos Aires University.\n\n'
ABOUT_TEXT += 'Free to use and expand.'