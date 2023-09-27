import glob
import ensemble_edf
import os

files = glob.glob(os.path.join("EDFfolder", "*.edf"))

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
    ensemble_edf.rename_for_ensemble(file)
