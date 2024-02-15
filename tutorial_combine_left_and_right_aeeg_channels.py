import ensemble_edf

# !!! change these variables to the paths to the left and right channels you
# !!! want to combine
path_2_left_channel = "/Users/bvelde3/_Research/EEG_Ensemble/EDF_scripts/Data/ANONYMOUS_20230630_RAW_F3.edf"
path_2_right_channel = "/Users/bvelde3/_Research/EEG_Ensemble/EDF_scripts/Data/ANONYMOUS_20230630_RAW_F4.edf"

ensemble_edf.combine_aeeg_channels(
    path_2_left_channel, path_2_right_channel, new_filename="two_channel_aeeg"
)
