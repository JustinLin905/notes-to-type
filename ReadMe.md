# NotesToType.py

NotesToType is a Python script which turns musical notes detected by the microphone into keyboard output. 

Dependencies for this program include `numpy`, `pyaudio`, `pyautogui`, and `audioop`.

An easy-to-use .exe file has been included, if you want to use the script out of the box with no Python installation.

# Usage

The default detectable note range is C4 (Middle C) to C5 (one octave above C4). The default functions of notes are below. Note that the black keys in this range are not assigned to anything by default.

* C4 -> COPY (CTRL + C)
* D4 -> PASTE (CTRL + V)
* E4 -> CUT (CTRL + X)
* F4 -> SeARCH ON PAGE (CTRL + F)
* G4 -> UNDO (CTRL + Z)
* A4 -> REDO (CTRL + Y)
* B4 -> SAVE (CTRL + S)
* C5 -> OPEN (CTRL + O)

Simply play a note that is at least **35dB** loud, and the function corresponding to the note will activate. Pure tones work best for accuracy, but instruments and voice can also be used to produce notes for the microphone (provided they are in tune).

# Editing

The functions assigned to notes can be modified to automate different keyboard and mouse outputs supported in `pyautogui`. For example, you can use notes to type characters or phrases.


The detectable note range can be changed as well, if you want to add more functions for more notes.


```
NOTE_MIN = 61       # C4
NOTE_MAX = 71       # C5
```

The value 61 corresponds to C4, and 71 corresponds to C5. Changing these values can widen or shorten the range of notes accepted by the program. Adding / subtracting one to `NOTE_MIN` or `NOTE_MAX` will move that note by a semitone in most cases. 