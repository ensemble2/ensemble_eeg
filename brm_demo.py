import glob
from importlib import reload
import brm_to_edf

reload(brm_to_edf)

files = glob.glob(
    "/Users/bvelde3/_Research/EEG_Ensemble/WKZ/Data/*.brm"
)  # Change this to where your BRM files are

for file in files:
    brm_to_edf.convert_brm_to_edf(file, is_fs_64hz=True)
