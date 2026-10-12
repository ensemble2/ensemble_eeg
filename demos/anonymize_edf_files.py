from pathlib import Path

from ensemble_eeg import ensemble_edf

# !!! change this to the location of the edf files you want to anonymize
path2edffiles = "/Users/bvelde3/_Research/EEG_Ensemble/WKZ/Data"

files = list(Path(path2edffiles).glob("*.edf"))

for file in files:
    ensemble_edf.fix_edf_header(file)  # fix edf header to edf+ standard
    ensemble_edf.anonymize_edf_header(file)  # anonymize edf header

    # rename edf file which was anonymized
    path_to_anon_file = file.with_name(f"{file.stem}_ANONYMIZED{file.suffix}")
    ensemble_edf.rename_for_ensemble(path_to_anon_file)
