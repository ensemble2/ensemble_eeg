import glob
import ensemble_edf
import os

# !!! change this to the location of the edf directory you want to change
path2edffiles = "path/2/edf/files"

files = glob.glob(os.path.join(path2edffiles, "*.edf"))

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
    # ensemble_edf.rename_for_ensemble(file)
