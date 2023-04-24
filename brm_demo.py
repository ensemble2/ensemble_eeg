import brm_to_edf
from importlib import reload
import glob
reload(brm_to_edf)

fd = '/Users/bauke/_Research/EEG_aEEG/0002_2.brm'

brm_to_edf.convert_brm_to_edf(fd)

