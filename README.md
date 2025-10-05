# A visual editor for Akai MPK2 series + a collection of command line scripts
Tested and reversed engineered on Akai MPK249. 
Usage on other controller of the MPK2 series is _untested_.
Scripts are a collection of command line tools for reading / writing single preset dump files

_Disclaimer:_ Use of this material can possibly void your warranty, corrupt your presets or brick your controller.

### Pre-requisites
For the GUI:
Install customtkinter (if not already installed)
```sh
pip install customtkinter pillow python-rtmidi
```
### Works that made this possible

https://github.com/nsmith-/mpk2

http://practicalusage.com/akai-mpk261-mpk2-series-controlling-the-controller-with-sysex/

http://practicalusage.com/akai-mpk261-one-more-thing/

http://www.akaipro.com/files/product_downloads/MPK2_Series_Bitwig_Scripts_v1.0.8.zip

## The GUI
Place this 3 files in the same directory

mpk249_gui.py

keyboard.jpg

mpk2_preset.py


Then run:

```sh
python akai_gui.py
```

#### Features:
Get Presets from Keyboard

Send Presets to Keyboard

Save and load from files

Set all parameters for pads

Set all parameters for knobs

Set all parameters for faders

Set all parameters for switches

Set all parameters for the 4 daw buttons

Bulk functions (midi channels, note settings, etc.)

#### Missing:
Transport 
Arpeggiator
Keyboard
Pitchebend / Modwheel

#### Usage with other MPK2 series keyboards (untested)

For midi support try edit port configurations mpk249_gui.py
```sh
self.MIDI_IN_GET_NAME = "MIDIIN4 (MPK249)"
self.MIDI_OUT_SEND_NAME = "MIDIOUT4 (MPK249)"
```
with your actual midi port names for sysex communications. (e.g. "MIDIIN4 (MPK269)" )

## Command-line scripts usage
To use the command line scripts in the scripts folder, you will need to already have a SINGLE preset dump file (.syx)
(do not use the "ALL" preset dump).

### Faders script

#### List values
python mpk2_fader_editor.py --import PRESET_FILE.syx --list-faders

Sample Output:

Fader  1 | Type=MIDI_CC    CC= 18 Ch= 0 Min=  0 Max=127 Din=Off

Fader  2 | Type=MIDI_CC    CC= 21 Ch= 0 Min=  0 Max=127 Din=Off

Fader  3 | Type=MIDI_CC    CC= 22 Ch= 0 Min=  0 Max=127 Din=Off

#### Set Value (set Fader 1 CC to 19)
python .\mpk2_fader_editor.py --import PRESET_FILE.syx  --set-fader 1 MIDI_CC 19 0 0 127 Off --export PRESET_FILE_NEW.syx

### Switches/Daw Buttons script
# List values
python mpk2_switch_daw_editor.py --import PRESET_FILE.syx --list-switches
# Set Values (set switch 1 channel to USBA1)
Python mpk2_switch_daw_editor.py --import PRESET_FILE.syx --set-switch 1 --type CC --channel USBA1 --export PRESET_FILE_NEW.syx

