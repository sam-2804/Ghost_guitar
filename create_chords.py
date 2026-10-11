import numpy as np
from scipy.io import wavfile

#To control the sustain of the chord
duration = 1.5
sample_rate = 44100
time_arr = np.linspace(0, duration, int(sample_rate * duration), False)

g_wave = np.sin(196.00 * 2 * np.pi * time_arr)
b_wave = np.sin(246.94 * 2 * np.pi * time_arr)
d_wave = np.sin(293.66 * 2 * np.pi * time_arr)

mixed_chord = (g_wave + b_wave + d_wave) / 3
fade = np.linspace(1, 0, len(time_arr))
final_audio = mixed_chord * fade


audio_data = np.int16(final_audio * 32767)
wavfile.write("chords\g_chord.wav", sample_rate, audio_data)
print("Cached g_chord.wav successfully!")

#TODO : Wrap this code into a function that accepts 3 frequencies of the any to generate a chord