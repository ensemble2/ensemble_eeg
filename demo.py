import glob
from importlib import reload

import ensemble_edf

reload(ensemble_edf)

files = glob.glob(
    '/Users/bauke/Downloads/Bauke ENSEMBLE/subj_101E000031/*.edf')

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)

fd = "/Users/bauke/Downloads/data/subj_101E100011/subj_101E100011_ses-diag_acq-aEEG_run-1_eeg.edf"

ensemble_edf.rename_for_ensemble(fd)
ensemble_edf.anonymize_edf_header(fd)
