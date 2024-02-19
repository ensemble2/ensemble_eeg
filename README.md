<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![PyPI version](https://badge.fury.io/py/ensemble-eeg.svg)](https://badge.fury.io/py/ensemble-eeg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<!-- ABOUT THE PROJECT -->
# ENSEMBLE EEG
Ensemble EEG is a library of EEG analyis tools for the ENSEMBLE study. As of
today it is focuses on 5 seperate things:

- **Anonymizing** EDF files in accordance with the ENSEMBLE study and the
  requirements of [EDF+](https://www.edfplus.info/specs/edfplus.html)
- **Fixing** EDF headers to adhere to the [EDF+](https://www.edfplus.info/specs/edfplus.html) standard
- **Converting** BRM to [EDF+](https://www.edfplus.info/specs/edfplus.html) files
- **Combining** seperate aEEG channels into one [EDF+](https://www.edfplus.info/specs/edfplus.html) file
- **Renaming** EEG files according to ENSEMBLE and [BIDS](https://bids-specification.readthedocs.io/en/stable/) standards

<!-- GETTING STARTED -->
## Getting started
### Prerequisites
The following is required for the use of this software
- **Python 3.10** & **pip**
  - For instructions, please refer to the following [link](https://github.com/PackeTsar/Install-Python/blob/master/README.md)

### Installation
```sh
python3 -m pip install ensemble_eeg
```

<!-- USAGE EXAMPLES -->
## Usage
#### Anonymizing EDF-files
```python
>>> from ensemble_eeg import ensemble_edf
>>> ensemble_edf.anonymize_edf_header('path/2/your/edf/file')
```
#### Fixing EDF headers
```python
>>> from ensemble_eeg import ensemble_edf
>>> ensemble_edf.fix_edf_header('path/2/your/edf/file')
```
#### Combine left and right aEEG channels into one single file
```python
>>> from ensemble_eeg import ensemble_edf
>>> ensemble_edf.combine_aeeg_channels('path/2/your/left/channel', 'path/2/your/right/channel', 'new_filename')
```
#### Rename EDF-files according to BIDS and ENSEMBLE standards
```python
>>> from ensemble_eeg import ensemble_edf
>>> ensemble_edf.rename_for_ensemble('path/2/your/edf/file')
```
### Examples for specific situations
##### 1) File is already EDF, but you do not know whether header is EDF+, the file is not anonymized, and not renamed
```python
>>> from ensemble_eeg import ensemble_edf
>>> file = 'path/2/your/edf/file'
>>> ensemble_edf.fix_edf_header(file)       # for header check
>>> ensemble_edf.anonymize_edf_header(file) # for anonymization
>>> ensemble_edf.rename_for_ensemble(file)  # for renaming

```
##### 2) File is BRM 
```python
>>> from ensemble_eeg import brm_to_edf
>>> from ensemble_eeg import ensemble_edf
>>> brm_file = 'path/2/your/brm/file'
>>> brm_to_edf.convert_brm_to_edf(brm_file)     # for conversion, output edf is already anonymized
>>> edf_file = 'path/2/your/edf/file'           # check which file was made in previous step
>>> ensemble_edf.rename_for_ensemble(edf_file)  # for renaming

```
##### 3) Files are edf, but left and right channel are seperate 
```python
>>> from ensemble_eeg import ensemble_edf
>>> left_file = 'path/2/your/left/edf/file'
>>> right_file = 'path/2/your/right/edf/file'
>>> ensemble_edf.combine_aeeg_channels(left_file, right_file) # output is automatically anonymized
>>> ensemble_edf.rename_for_ensemble(file)                    # for renaming

```
##### 4) Anonymize multiple edf files in the same directory 
```python
>>> from ensemble_eeg import ensemble_edf
>>> import glob
>>> import os
>>> edf_directory = 'path/2/your/left/edf/directory'
>>> edf_files = glob.glob(os.path.join(edf_directory, "*.edf"))
>>> for file in edf_files:
      ensemble_edf.fix_edf_header(file) 
      ensemble_edf.anonymize_edf_header(file) 
      ensemble_edf.rename_for_ensemble(file)                    
```
##### 5) Convert multiple BRM files in the same directory 
```python
>>> from ensemble_eeg import brm_to_edf
>>> import glob
>>> import os
>>> brm_directory = 'path/2/your/left/edf/directory'
>>> brm_files = glob.glob(os.path.join(brm_directory, "*.brm"))
>>> for file in brm_files:
      brm_to_edf.convert_brm_to_edf(file) 
```

<!-- ACKNOWLEDGMENTS -->
## Acknowledgements
- [edfrd](https://github.com/somnonetz/edfrd)
- [Install-Python-Instructions](https://github.com/PackeTsar/Install-Python/tree/master)
