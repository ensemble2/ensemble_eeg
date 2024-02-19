from ensemble_eeg import ensemble_edf

# !!! change these variables to the paths to the left and right channels you
# !!! want to combine
path_2_left_channel = "path/2/left/channel.edf"
path_2_right_channel = "path/2/right/channel.edf"

ensemble_edf.combine_aeeg_channels(
    path_2_left_channel, path_2_right_channel, new_filename="two_channel_aeeg"
)
