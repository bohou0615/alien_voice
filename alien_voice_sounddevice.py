##########################################################################
# REFERENCE:
#     E. Bezzam, A. Hoffet, P. Prandoni,
#     Teaching Practical DSP with Off-the-Shelf Hardware and Free Software,
#     Proc. IEEE ICASSP, Brighton, UK, 2019.
##########################################################################
#
# file <alien_voice_effect>
# brief <generate alien voice with with your laptop's soundcard
# author <Danny Wu>
# date <Jul 4 2022>

import sounddevice as sd
import numpy as np
from utils import build_sine_table


# parameters
buffer_len = 256
f_sine = 200   # Hz, for modulation
high_pass_on = False

data_type = np.int16
samp_freq = 16000

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % data_type)

# allocate input and output buffers
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)

# state variables
def init():
    global sine_pointer
    global x_prev
    global GAIN
    global SINE_TABLE
    global MAX_SINE
    global LOOKUP_SIZE

    GAIN = 1
    x_prev = 0
    sine_pointer = 0

    # compute SINE TABLE
    vals = build_sine_table(f_sine, samp_freq, data_type=data_type)
    SINE_TABLE = vals[0]
    MAX_SINE = vals[1]
    LOOKUP_SIZE = vals[2]


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    global x_prev
    global sine_pointer

    for n in range(buffer_len):

        # high pass filter
        if high_pass_on:
            output_buffer[n] = input_buffer[n] - x_prev
        else:
            output_buffer[n] = input_buffer[n]

        output_buffer[n] = input_buffer[n] * SINE_TABLE[sine_pointer] / MAX_SINE

        sine_pointer += 1
        sine_pointer %= LOOKUP_SIZE
        x_prev = output_buffer[n]


"""
Nothing to touch after this!
"""
try:
    sd.default.device = [4,6]  #check your own device[input, output] by 'python3 -m sounddevice'
    sd.default.samplerate = samp_freq
    sd.default.blocksize = buffer_len
    sd.default.dtype = data_type

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        process(indata[:, 0], outdata[:, 0], frames)

    init()
    with sd.Stream(channels=2, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    print('\nInterrupted by user')

