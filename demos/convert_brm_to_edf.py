import glob

from ensemble_eeg import brm_to_edf

# !!! change this to the location of the brm files you want to convert
files = glob.glob("path/2/brm/files")

for file in files:
    brm_to_edf.convert_brm_to_edf(file, is_fs_64hz=True)
