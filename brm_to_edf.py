import zipfile
import defusedxml.ElementTree as ET
from collections import Counter
import glob
import os
from collections import namedtuple
import shutil
import numpy as np
from datetime import datetime, timezone
import ensemble_edf

fd = "/Users/bauke/_Research/aEEG_check/115-044-249-1_1_1_RAW.brm"


def convert_brm_to_edf(fd, is_fs_64hz=None):
    filename = os.path.basename(fd)
    file_exists = os.path.isfile(fd)

    if file_exists:
        file_dir = os.path.dirname(fd)
        tmp_dir = os.path.join(file_dir, 'tmp')
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

        print(f'{filename}')
        print(f'\tUnzipping to temporary directory')
        with zipfile.ZipFile(fd, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        index_xml = os.path.join(tmp_dir, 'BRM_Index.xml')
        index = parse_xml(index_xml)
        device_xml = os.path.join(tmp_dir, 'device.xml')
        device = parse_xml(device_xml)

        dat_files = []
        if is_fs_64hz == None:
            is_fs_64hz =\
                input('is the sampling frequency 64 Hz? [y/N]: ').lower() == 'y'

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

        for i in range(0, n_data_files_left):
            both_dat_files = [dat_files_left[i], dat_files_right[i]]
            data = extract_brm_file(index, device, both_dat_files)

            if i == 0:
                output_filename = os.path.splitext(fd)[0] + '.edf'
            else:
                output_filename = os.path.splitext(fd)[0] + '_' + str(i) +\
                    '.edf'

            hdr = prepare_edf_header(data)
            signal_header = prepare_edf_signal_header(data, device)
            header = ensemble_edf.Header(*hdr, signal_header)

            # write header to file
            print(f'\tprint header to {output_filename}')
            ensemble_edf.write_edf_header(output_filename, header)

            # write data to file
            print(f'\tprint data records to {output_filename}')
            write_brm_data_to_edf(output_filename, data)

        print('\tremoving temporary directory')
        shutil.rmtree(tmp_dir)
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
                counter = counter + 1
            else:
                parsed_child = []
                child_elems = root.findall(name)
                for child_elem in child_elems:
                    child_elem_tags = [el.tag for el in child_elem]
                    child_elem_vals = [el.text for el in child_elem]
                    tup = namedtuple(child_elem.tag, child_elem_tags)
                    parsed_child.append(tup(*child_elem_vals))
                    counter = counter + 1
                parsed_xml.append(parsed_child)

    else:
        raise ValueError('file not found')

    return Parsed_XML(*parsed_xml)


def extract_brm_file(index, device, dat_files):
    filenames = [fd.FileName for fd in index.FileDescription]

    counter = 0
    data = [[] for _ in dat_files]

    for dat_file in dat_files:
        df = os.path.basename(dat_file)
        file = index.FileDescription[filenames.index(df)]
        file = file._replace(FileName=dat_file)
        print(f'\textracting {df} datastream')
        data[counter] = get_brm_data(file, device)
        counter = counter + 1

    return data


def get_brm_data(file, device):
    DAUSampleHz = 512

    Data = namedtuple('data', list(file._fields) + ['sampleHz', 'data'])
    data = list(file)
    data.append(int(DAUSampleHz / int(file.SamplePeriod512thSeconds)))
    data.append(get_numerical_data(file, device))

    return Data(*data)


def get_numerical_data(file, device):
    f = open(file.FileName, 'rb')

    match file.FileType:
        case 'FloatMappedToInt16' | 'Int16':
            data = np.fromfile(f, dtype=np.int16)
        case 'Float32':
            data = np.fromfile(f, dtype=np.float32)
        case _:
            raise Exception(f'Unrecognized file format {file.FileType}')

    return data


def prepare_edf_header(data):
    n_channels = 2
    version = '0'
    PID = 'X X X X'
    RID = 'Startdate X X X X'
    start_date = datetime.strftime(
        datetime.fromtimestamp(int(data[0].StartTime),
                               timezone.utc), format='%d.%m.%y')
    start_time = datetime.strftime(
        datetime.fromtimestamp(int(data[0].StartTime),
                               timezone.utc), format='%H.%M.%S')
    bytes_in_header = ensemble_edf.HEADER_SIZE + n_channels *\
        ensemble_edf.SIGNAL_HEADER_SIZE
    reserved = None
    fs = data[0].sampleHz
    n_records = int(np.floor(len(data[0].data)/fs))
    dur_data_record = '1'
    n_signals = len(data)
    header = [version, PID, RID, start_date, start_time, bytes_in_header,
              reserved, n_records, dur_data_record, n_signals]

    return header


def prepare_edf_signal_header(data, device):
    channel_ids = [channel.ID for channel in device.Channel]
    units = data[0].Units

    # replace non-ascii characters
    if 'µ' in units:
        units = units.replace('µ', 'u')

    signal_headers = [[] for _ in data]
    for i in range(0, len(data)):
        ichan = channel_ids.index(data[i].ChannelTitle)
        if data[i].ChannelTitle == 'Left':
            label = 'F3'
        else:
            label = 'F4'

        transducer_type = None
        physical_dimension = units
        physical_min = round(-5e6 / float(device.Channel[ichan].Gain) / 2)
        physical_max = round(5e6 / float(device.Channel[ichan].Gain) / 2)
        digital_min = -(2**15-1)
        digital_max = (2**15-1)
        prefiltering = None
        nr_samples = data[i].sampleHz
        reserved = None
        sig_header = [label, transducer_type, physical_dimension,
                      physical_min, physical_max, digital_min,
                      digital_max, prefiltering, nr_samples,
                      reserved]
        signal_headers[i] = ensemble_edf.SignalHeader(*sig_header)

    return tuple(signal_headers)


def write_brm_data_to_edf(filename, data):
    file_exists = os.path.isfile(filename)
    dat1 = data[0].data
    dat2 = data[1].data

    if file_exists:
        fs = data[0].sampleHz
        n_records = int(np.floor(len(data[0].data)/fs))
        fd = open(filename, 'ab')

        index = 0
        for i_record in range(0, n_records):
            fd.write(dat1[index:(index+fs)])
            fd.write(dat2[index:(index+fs)])
            index = (i_record + 1) * fs

        fd.close()
