import glob
from importlib import reload
import ensemble_edf

reload(ensemble_edf)

files = glob.glob("/Users/bvelde3/_Research/aEEG_check/subj-101E000021/*.edf")

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
    ensemble_edf.rename_for_ensemble(file)
