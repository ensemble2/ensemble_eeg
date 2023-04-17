import ensemble_edf
from importlib import reload
import glob
reload(ensemble_edf)

files = glob.glob(
    '/Users/bauke/Downloads/Bauke ENSEMBLE/subj_101E000031/*.edf')

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
