import glob
from importlib import reload

import brm_to_edf

reload(brm_to_edf)

files = glob.glob('/Users/bauke/_Research/EEG_aEEG/*.brm')
files = files[0:3]

for file in files:
    brm_to_edf.convert_brm_to_edf(file, is_fs_64hz=False)
