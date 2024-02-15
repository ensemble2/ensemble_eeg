import glob
import brm_to_edf

# !!! change this to the location of the brm files you want to convert
files = glob.glob(
    "/Users/bvelde3/_Research/EEG_Ensemble/WKZ/Data/*.brm"
)  # Change this to where your BRM files are

for file in files:
    brm_to_edf.convert_brm_to_edf(file, is_fs_64hz=True)
