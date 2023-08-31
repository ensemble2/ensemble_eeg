import ensemble_edf
from importlib import reload
import glob
reload(ensemble_edf)

files = glob.glob(
    '/path/to/edffiles/*.edf')

for file in files:
    ensemble_edf.fix_edf_header(file)
    ensemble_edf.anonymize_edf_header(file)
    ensemble_edf.rename_for_ensemble(file)
