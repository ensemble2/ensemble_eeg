import glob
from importlib import reload
import brm_to_edf
import os

reload(brm_to_edf)

files = glob.glob(
    "/Users/bvelde3/SCORED/*.brm"
)  # Change this to where your BRM files are
files = files[0:1]

for file in files:
    brm_to_edf.convert_brm_to_edf(file, is_fs_64hz=False)
