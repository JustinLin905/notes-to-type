######################################################################

# NotesToType.py  :  a script which turns notes detected by the 
# microphone into keyboard output. 

# Dependencies: numpy, pyaudio, pyautogui, audioop

# The default configuration for notes are:

# C4 -> COPY (CTRL + C)
# D4 -> PASTE (CTRL + V)
# E4 -> CUT (CTRL + X)
# F4 -> SeARCH ON PAGE (CTRL + F)
# G4 -> UNDO (CTRL + Z)
# A4 -> REDO (CTRL + Y)
# B4 -> SAVE (CTRL + S)
# C5 -> OPEN (CTRL + O)

# These functions can be changed to automate different keyboard
# or mouse outputs supported in pyautogui. The note range can 
# also be edited. Pure tones work best for accuracy, but instruments
# and voice can also be used.

# This script was built on top of tuner.py, a ukelele tuner 
# written by Matt Zucker in 2016. On top of this framework, 
# I added decibel detection, keyboard atuomation, and other 
# optimizations to make it better suited for converting notes 
# into keyboard output.
 
# Feel free to reuse, edit, or transform this script into
# whatever you like!

# Written by Justin Lin in July 2020

######################################################################








######################################################################
# tuner.py - a minimal command-line guitar/ukulele tuner in Python.
# Requires numpy and pyaudio.
######################################################################
# Author:  Matt Zucker
# Date:    July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#          https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################

import numpy as np
import pyaudio
from time import sleep
import pyautogui
import audioop
import math


# Non-repeat variables: used to prevent notes from unintentionally repeating key presses
c4 = False
d4 = False
e4 = False
f4 = False
g4 = False
a4 = False
b4 = False
c5 = False


# Non-repeat timers, used in timing for this same purpose
inputDelayTimer = 0
nonRepeatTimer = 0

# These constants determine how long the above timers must run in order to finish
INPUT_DELAY_LIMIT = 8
NON_REPEAT_DELAY = 7



# Decibel limit, used to control what volume notes must reach to trigger output
DECIBEL_LIMIT = 35

# Freq variable, used to store the frequency of input from the microphone
freq = 1

######################################################################
# Feel free to play with these numbers. Might want to change NOTE_MIN
# and NOTE_MAX especially for guitar/bass. Probably want to keep
# FRAME_SIZE and FRAMES_PER_FFT to be powers of two.

# Note: NOTE_MIN AND NOTE_MAX determine the lowest and highest notes the
# tuner can detect. Example: if you lower NOTE_MIN by 1, the lowest detectable 
# note goes down by one semitone in most cases. If you increase one of those variables, vice-versa.

NOTE_MIN = 61       # C4
NOTE_MAX = 71       # C5
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

######################################################################
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (so
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

######################################################################
# Note names for printing out notes

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)


######################################################################
# Ok, ready to go now.

# Get min/max index within FFT of notes we care about.
# See docs for numpy.rfftfreq()
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

# Allocate space to run an FFT. 
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# Initialize audio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)

stream.start_stream()

# Create Hanning window function
window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

# Print initial text
print('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')
print()

# As long as we are getting data:
while stream.is_active:

    # Shift the buffer down and new data in
    buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
    buf[-FRAME_SIZE:] = np.frombuffer(stream.read(FRAME_SIZE), np.int16)

    # Run the FFT on the windowed buffer
    fft = np.fft.rfft(buf * window)

    # Decibel and RMS variables: used to determine if sound is loud enough
    data = stream.read(FRAME_SIZE)
    rms = audioop.rms(data,2) + 1                   # The '+ 1' is to prevent any log errors when taking the log of 0, but may reduce accuracy

    # Equation to obtain volume of noise from mic in decibels
    decibel = 20 * math.log10(rms)




    ### Get frequency of maximum response in range ###

    # If the noise from mic is loud enough...
    if decibel > DECIBEL_LIMIT:

        # Start adding to this timer. This creates a small delay to increase the accuracy of readings.
        inputDelayTimer += 1

        # Once the timer is up...
        if inputDelayTimer == INPUT_DELAY_LIMIT:

            # Take the frequency of the input from the mic
            freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP
            inputDelayTimer = 0

    # If the input from the mic is not loud enough...
    else:

        # Set freq to 1 to prevent accidental outputs
        freq = 1



    # Get note number and nearest note
    n = freq_to_number(freq)
    n0 = int(round(n))

    # Console output once we have a full buffer
    num_frames += 1

    # If freq is being taken from the mic, print to the console the detected freq, note, number, cents, etc.
    if freq != 1:
        if num_frames >= FRAMES_PER_FFT:
            print('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
                freq, note_name(n0), n-n0))

    # If freq is not being taken from the mic
    else:

        print("No note detected.")


















    ### TURN DETECTED NOTES INTO KEYBOARD OUTPUT ###
    if decibel > DECIBEL_LIMIT:

        # C4 -> COPY
        if 253 <= freq <= 270 and decibel > DECIBEL_LIMIT and c4 == False:

            pyautogui.hotkey("ctrl", "c")

        # D4 -> PASTE
        elif 290 <= freq <= 300 and decibel > DECIBEL_LIMIT and d4 == False:

            pyautogui.hotkey("ctrl", "v")
            d4 = True
            sleep (1)


        # E4 -> CUT
        elif 320 <= freq <= 335 and decibel > DECIBEL_LIMIT and e4 == False:

            pyautogui.hotkey("ctrl", "x")
            e4 = True

        # F4 -> SeARCH ON PAGE (CTRL + F)
        elif 345 <= freq <= 360 and decibel > DECIBEL_LIMIT and f4 == False:

            pyautogui.hotkey("ctrl", "f")
            f4 = True

        # G4 -> UNDO
        elif 380 <= freq <= 405 and decibel > DECIBEL_LIMIT and g4 == False:

            pyautogui.hotkey("ctrl", "z")
            g4 = True

        # A4 -> REDO
        elif 431 <= freq <= 450 and decibel > DECIBEL_LIMIT and a4 == False:

            pyautogui.hotkey("ctrl", "y")
            a4 = True

        # B4 -> SAVE
        elif 480 <= freq <= 500 and decibel > DECIBEL_LIMIT and b4 == False:

            pyautogui.hotkey("ctrl", "s")
            b4 = True

        # C5 -> OPEN
        elif 515 <= freq <= 535 and decibel > DECIBEL_LIMIT and c5 == False:

            pyautogui.hotkey("ctrl", "o")
            c5 = True
















    #################################################


    # Add one to this timer every time data from the microphone is taken and printed
    if decibel > DECIBEL_LIMIT:

        nonRepeatTimer += 1


    # This if statement helps prevent key output from repeating from one note input
    if nonRepeatTimer == NON_REPEAT_DELAY:

        # Allow notes to trigger output again
        c4 = False
        d4 = False
        e4 = False
        f4 = False
        g4 = False
        a4 = False
        b4 = False
        c5 = False

        # Reset this timer
        nonRepeatTimer = 0