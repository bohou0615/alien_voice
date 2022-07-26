##########################################################################
# REFERENCE:
#     E. Bezzam, A. Hoffet, P. Prandoni,
#     Teaching Practical DSP with Off-the-Shelf Hardware and Free Software,
#     Proc. IEEE ICASSP, Brighton, UK, 2019.
##########################################################################
#
# file <alien_voice_effect>
# brief <generate alien voice with given parameters(freq...)
# author <Danny Wu>
# date <Jul 4 2022>



from scipy.io import wavfile
import os
import numpy as np
from utils import build_sine_table


# parameters
buffer_len = 256
f_sine = 200   # Hz, for modulation
high_pass_on = True

# test signal
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
if len(signal.shape) > 1:
    signal = signal[:, ]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % signal.dtype)

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
init()
# simulate block based processing
signal_proc = np.zeros(n_buffers*buffer_len, dtype=data_type)
for k in range(n_buffers):

    # index the appropriate samples
    input_buffer = signal[k*buffer_len:(k+1)*buffer_len]
    process(input_buffer, output_buffer, buffer_len)
    signal_proc[k*buffer_len:(k+1)*buffer_len] = output_buffer

# write to WAV
wavfile.write("alien_voice_effect.wav", samp_freq, signal_proc)
