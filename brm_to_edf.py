import zipfile
import defusedxml.ElementTree as ET
from collections import Counter
import glob
import os
from collections import namedtuple


def convert_brm_to_edf(fd):
    file_exists = os.path.isfile(fd)

    if file_exists:
        file_dir = os.path.dirname(fd)
        tmp_dir = os.path.join(file_dir, 'tmp')

        with zipfile.ZipFile(fd, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        index_xml = os.path.join(tmp_dir, 'BRM_Index.xml')
        index = parse_xml(index_xml)
        device_xml = os.path.join(tmp_dir, 'device.xml')
        device = parse_xml(device_xml)

        dat_files = []
        is_fs_64hz = input('is the sampling frequency 64 Hz? [y/N]') == 'y'
        if is_fs_64hz:
            dat_files.append(glob.glob(
                os.path.join(tmp_dir, 'DATA_RAW_EEG_LEFT*.dat')))
            dat_files.append(glob.glob(
              os.path.join(tmp_dir, 'DATA_RAW_EEG_RIGHT*.dat')))
        else:
            dat_files_left = glob.glob(
                os.path.join(tmp_dir, 'DATA_RAW_EEG_ELECTRODE_LEFT*.dat'))
            dat_files_right = glob.glob(
                os.path.join(tmp_dir, 'DATA_RAW_EEG_ELECTRODE_RIGHT*.dat'))

        n_data_files_left = len(dat_files_left)
        n_data_files_right = len(dat_files_right)

        assert n_data_files_left == n_data_files_right

        dat_files = dat_files_left + dat_files_right

        # TODO: finish up this piece of code
    else:
        raise ValueError('file not found')


def parse_xml(xml):
    file_exists = os.path.isfile(xml)

    if file_exists:
        tree = ET.parse(xml)
        root = tree.getroot()

        all_tags = [child.tag for child in root]
        tag_names = list(Counter(all_tags).keys())
        tag_dict = list(Counter(all_tags).items())

        Parsed_XML = namedtuple('ParsedXML', tag_names)
        parsed_xml = []
        counter = 0
        for name, vals in tag_dict:
            if vals == 1:
                parsed_xml.append(root[counter].text)
            else:
                parsed_child = []
                child_elems = root.findall(name)
                for child_elem in child_elems:
                    child_elem_tags = [el.tag for el in child_elem]
                    child_elem_vals = [el.text for el in child_elem]
                    tup = namedtuple(child_elem.tag, child_elem_tags)
                    parsed_child.append(tup(*child_elem_vals))
                parsed_xml.append(parsed_child)

    else:
        raise ValueError('file not found')

    return Parsed_XML(*parsed_xml)


def extract_brm_file(index, device, tmp_dir_path, dat_files):
    filenames = [fd.FileName for fd in index.FileDescription]

    counter = 0
    for dat_file in dat_files:
        df = os.path.basename(dat_file)
        print(f'Extracting {df} datastream')
        data[counter] = \
            get_brm_data(index.FileDescription[filenames.index(df)],
                         tmp_dir_path, device)

    # TODO: finish up this piece of code


def get_brm_data(file, tmp_dir_path, device):
    DAUSampleHz = 512

    Data = namedtuple('data', list(file._fields) + ['sampleHz', 'data'])
    data = list(file)
    data.append(int(DAUSampleHz / int(file.SamplePeriod512thSeconds)))

    # TODO: finish up this piece of code
