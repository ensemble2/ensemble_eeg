import glob
import os
import ensemble_edf

# !!! change this to the location of the edf files you want to anonymize
path2edffiles = "/Users/bvelde3/_Research/EEG_Ensemble/EDF_scripts/Data"
files = glob.glob(os.path.join(path2edffiles, "*.edf"))

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
    # ensemble_edf.rename_for_ensemble(file)
