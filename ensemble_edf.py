import os
import shutil
import warnings
from collections import namedtuple

import numpy as np


def _str(f, size, _):
    s = f.read(size).decode('ascii', 'ignore').strip()
    while s.endswith('\x00'):
        s = s[:-1]
    return s


def _int(f, size, name):
    s = _str(f, size, name)
    try:
        return int(s)
    except ValueError:
        warnings.warn('{name}: Could not parse integer {s}.'
                      .format(name=name, s=s))


def _float(f, size, name):
    s = _str(f, size, name)
    try:
        return float(s)
    except ValueError:
        warnings.warn('{name}: Could not parse float {s}.'
                      .format(name=name, s=s))


def _discard(f, size, _):
    f.read(size)


HEADER = (
    ('version', 8, _str),
    ('local_patient_identification', 80, _str),
    ('local_recording_identification', 80, _str),
    ('startdate_of_recording', 8, _str),
    ('starttime_of_recording', 8, _str),
    ('number_of_bytes_in_header_record', 8, _int),
    ('reserved', 44, _discard),
    ('number_of_data_records', 8, _int),
    ('duration_of_a_data_record', 8, _float),
    ('number_of_signals', 4, _int),
)


SIGNAL_HEADER = (
    ('label', 16, _str),
    ('transducer_type', 80, _str),
    ('physical_dimension', 8, _str),
    ('physical_minimum', 8, _float),
    ('physical_maximum', 8, _float),
    ('digital_minimum', 8, _int),
    ('digital_maximum', 8, _int),
    ('prefiltering', 80, _str),
    ('nr_of_samples_in_each_data_record', 8, _int),
    ('reserved', 32, _discard)
)

INT_SIZE = 2
HEADER_SIZE = sum([size for _, size, _ in HEADER])
SIGNAL_HEADER_SIZE = sum([size for _, size, _ in SIGNAL_HEADER])

Header = namedtuple('Header', [name for name, _, _ in HEADER] + ['signals'])
SignalHeader = namedtuple('SignalHeader', [name for name, _, _ in
                                           SIGNAL_HEADER])


def read_edf_header(fd):
    opened = False
    if isinstance(fd, str):
        opened = True
        fd = open(fd, 'rb')

    header = [func(fd, size, name) for name, size, func in HEADER]
    number_of_signals = header[-1]
    signal_headers = [[] for _ in range(number_of_signals)]

    for name, size, func in SIGNAL_HEADER:
        for signal_header in signal_headers:
            signal_header.append(func(fd, size, name))

    header.append(tuple(SignalHeader(*signal_header) for signal_header in
                        signal_headers))

    if opened:
        fd.close()

    return Header(*header)


def read_edf_data(fd, header):
    opened = False
    if isinstance(fd, str):
        opened = True
        fd = open(fd, 'rb')

        start = 0
        end = header.number_of_data_records
        data_record_length = sum([signal.nr_of_samples_in_each_data_record
                                  for signal in header.signals])

        if opened:
            fd.seek(HEADER_SIZE + header.number_of_signals *
                    SIGNAL_HEADER_SIZE + start * data_record_length * INT_SIZE)

        for _ in range(start, end):
            a = np.fromfile(fd, count=data_record_length, dtype=np.int16)

            data_record = []
            offset = 0

            for signal in header.signals:
                data_record.append(a[offset:offset +
                                     signal.nr_of_samples_in_each_data_record])
                offset += signal.nr_of_samples_in_each_data_record

        yield data_record

    if opened:
        fd.close()


def write_edf_header(fd, header):
    opened = False
    if isinstance(fd, str):
        fd = open(fd, 'wb')
        opened = True

        for val, (name, size, _) in zip(header, HEADER):
            if val is None:
                val = b'\x20' * size

            if not isinstance(val, bytes):
                if (name == 'startdate_of_recording' or name ==
                        'starttime_of_recording') and not isinstance(val, str):
                    val = '{:02d}.{:02d}.{:02d}'.format(
                        val[0], val[1], val[2] % 100)
                val = str(val).encode(encoding='ascii').ljust(size, b'\x20')

            assert len(val) == size
            fd.write(val)

        for vals, (name, size, _) in zip(zip(*header.signals), SIGNAL_HEADER):
            for val in vals:
                if val is None:
                    val = b'\x20' * size

                if not isinstance(val, bytes):
                    val = str(val).encode(
                        encoding='ascii').ljust(size, b'\x20')

                assert len(val) == size
                fd.write(val)

    if opened:
        fd.close()


def write_edf_data(fd, data_records):
    """Function to check and fix edf files according to EDF plus standards

    Args:
        fd (str): (Relative) path to file to write.
        data_records (array): Variable with data_records to write to edf file\
            is output from read_edf_data function

    """
    opened = False
    if isinstance(fd, str):
        opened = True
        fd = open(fd, 'ab')

    try:
        for data_record in data_records:
            for signal in data_record:
                signal.tofile(fd)
    finally:
        if opened:
            fd.close()


def fix_edf_header(fd):
    """Function to check and fix edf files according to EDF plus standards

    Args:
        fd (str): (Relative) path to file to rename.

    """
    header = read_edf_header(fd)
    data = read_edf_data(fd, header)

    something_to_fix = False
    if ":" in header.startdate_of_recording:
        warnings.warn(f'start date {header.startdate_of_recording} '
                      'contains colon (:), changing to dot (.)')
        header = header._replace(startdate_of_recording=header.
                                 startdate_of_recording.replace(':', '.'))
        something_to_fix = True

    if ":" in header.starttime_of_recording:
        warnings.warn(f'start time {header.starttime_of_recording}'
                      'contains colon (:), changing to dot (.)')
        header = header._replace(starttime_of_recording=header.
                                 starttime_of_recording.replace(':', '.'))
        something_to_fix = True

    for signal in header.signals:
        if signal.physical_maximum <= signal.physical_minimum:
            warnings.warn(f'channel {signal.label}: physical maximum '
                          f'({signal.physical_maximum}) is smaller or equal '
                          f'to physical minimum ({signal.physical_minimum})')

        if signal.digital_maximum <= signal.digital_minimum:
            warnings.warn(f'channel {signal.label}: digital maximum '
                          f'({signal.digital_maximum}) is smaller or equal '
                          f'to digital minimum ({signal.digital_minimum})')

    if something_to_fix:
        tmp_fd = fd + "tmp"
        write_edf_header(tmp_fd, header)
        write_edf_data(tmp_fd, data)

        assert os.path.getsize(tmp_fd) == os.path.getsize(fd)
        os.replace(tmp_fd, fd)


def anonymize_edf_header(fd):
    """Function to anonymize edf files according to ENSEMBLE and BIDS standards

    Args:
    fd (str): (Relative) path to file to rename.

    """
    header = read_edf_header(fd)
    data = read_edf_data(fd, header)

    filename = os.path.basename(fd)
    split_filename = filename.split('_')
    is_ensemble_approved = split_filename[0] == 'subj' and \
        len(split_filename[1]) == 10 and ('E' in split_filename[1])

    anonymized_rid = 'Startdate X X X X'
    if is_ensemble_approved:
        pseudo_code = split_filename[1]
        anonymized_pid = pseudo_code + ' X X X'
    else:
        anonymized_pid = 'X X X X'

    anonymized_startdate = '01.01.85'
    anonymized_starttime = '00.00.00'

    header = header._replace(local_patient_identification=anonymized_pid,
                             local_recording_identification=anonymized_rid,
                             startdate_of_recording=anonymized_startdate,
                             starttime_of_recording=anonymized_starttime)

    tmp_fd = fd + 'tmp'
    write_edf_header(tmp_fd, header)
    write_edf_data(tmp_fd, data)

    assert os.path.getsize(tmp_fd) == os.path.getsize(fd)
    os.replace(tmp_fd, fd)


def rename_for_ensemble(fd):
    """Function to rename edf files according to ENSEMBLE and BIDS standards

    Args:
        fd (str): (Relative) path to file to rename.

    """
    if not os.path.isfile(fd):
        raise FileNotFoundError("No such file or directory")

    filedir = os.path.expanduser(os.path.dirname(fd))
    if not filedir:
        filedir = os.getcwd()

    while True:
        print(f'changing name of {fd}')
        filename = os.path.basename(fd)

        # check whether filename needs to be changed
        do_renaming = check_filename_ensemble(filename)

        if do_renaming:
            header = read_edf_header(fd)

            # get the new subject code
            subject_code = get_subject_code()

            # check type of acquisition
            acq = get_acquisition_type(header)

            # check type of session
            ses = get_session_type()

        split_new_filename = ['subj', subject_code, ses, acq, 'run-1_eeg.edf']
        new_filename = "_".join(split_new_filename)

        print(f'new filename is {new_filename}')
        correct_filename = input('Is this correct? [Y/n]: ')

        if correct_filename.lower() == 'y':
            break

    # Create new directory and copy renamed file
    new_dirname = os.path.join(filedir, "_".join(split_new_filename[0:2]))
    new_filename = os.path.join(new_dirname, new_filename)

    if not os.path.isdir(new_dirname):
        os.mkdir(new_dirname)

    if os.path.isfile(new_filename):
        raise FileExistsError("File already exists, not overwriting")
    else:
        shutil.copy(fd, new_filename)


def check_filename_ensemble(filename):
    """
    Helper function to check filename and compare to the ENSEMBLE standard
    """
    split_filename = filename.split('_')
    do_renaming = True

    if ((split_filename[0] == 'subj') and
            ('ses' in split_filename[2]) and
            ('acq' in split_filename[3]) and
            ('run' in split_filename[4]) and
            (split_filename[-1] == 'eeg.edf')):
        do_renaming = False
        warnings.warn('The filename already seems to adhere to the ensemble '
                      'and BIDS standard ')
        continue_renaming = input('Are you sure you want to rename this file? '
                                  '[y/N]')
        do_renaming = continue_renaming.lower() == 'y'

    return do_renaming


def get_subject_code():
    """
    Helper code to get subject code with user input
    """

    # Get centre code
    while True:
        centre_code = input('Please input your centre code [xxx]: ')
        if len(centre_code) != 3 or not centre_code.isdigit():
            print('Centre code must consist of three digits')
            continue
        break

    # Get subject number
    while True:
        subject_number = input('Please input your subject number [xxxxx]: ')
        if len(subject_number) != 5 or not subject_number.isdigit():
            print('Subject number must consist of five digits')
            continue
        break

    # Get sibling number
    while True:
        sibling_number = input('Please input the sibling number [x]: ')
        if len(sibling_number) != 1 or not sibling_number.isdigit():
            print('Sibling number must consist of a single digit')
            continue
        break

    subject_code = centre_code + 'E' + subject_number + sibling_number

    return subject_code


def get_acquisition_type(header):
    """
    Helper code to get acquisition type with user input
    """

    # Check number of signals in file
    if header.number_of_signals <= 4:
        acq = 'acq-aeeg'
        print('file automatically determined to be aEEG')
        correct_acq = input('is this correct? [Y/n]: ').lower()

        if correct_acq == 'n':
            acq = 'acq-ceeg'

    else:
        acq = 'acq-ceeg'
        print('file automatically determined to be cEEG')
        correct_acq = input('is this correct? [Y/n]: ').lower()

        if correct_acq == 'n':
            acq = 'acq-aeeg'

    return acq


def get_session_type():
    """
    Helper code to get session type with user input
    """
    while 1:
        ses_string = 'During which session was this recordig taken? ' +\
                    '[(d)iag/(t)erm]: '
        ses = input(ses_string).lower()
        if ses == 'd' or ses == 'diag':
            ses = 'ses-diag'
            break
        elif ses == 't' or ses == 'term':
            ses = 'ses-term'
            break

    return ses
