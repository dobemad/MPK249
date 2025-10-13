# A visual editor for Akai MPK2 series + a collection of command line scripts
Tested and reversed engineered on Akai MPK249. 
Usage on other controller of the MPK2 series is _untested_.
Scripts are a collection of command line tools for reading / writing single preset dump files

_Disclaimer:_ Use of this material can possibly void your warranty, corrupt your presets or brick your controller.

## Downloads
If you are not familiar with setting up a python environment 

you can download the Windows executable from this repository [here](https://github.com/dobemad/MPK249/releases/download/v1.0.0/mpk249_gui.exe).
(sorry Apple users)

### Pre-requisites for running the source code:
For the GUI:
Install customtkinter (if not already installed) pillow and python-rtmidi
```sh
pip install customtkinter pillow python-rtmidi
```
Download Akai media images (for the gui)

https://cdn.inmusicbrands.com/akai/attachments/MPK249/MPK249%20-%20Media.zip

And extract MPK249_ortho_10x8_media_01.jpg

### Works that made this possible

https://github.com/nsmith-/mpk2

http://practicalusage.com/akai-mpk261-mpk2-series-controlling-the-controller-with-sysex/

http://practicalusage.com/akai-mpk261-one-more-thing/

https://cdn.inmusicbrands.com/akai/attachments/MPK249/MPK2_Series_Bitwig_Scripts_v1.0.8.zip

## Running the GUI in python

Place this 3 files in the same directory

mpk249_gui.py

mpk2_preset.py

Renamed MPK249_ortho_10x8_media_01.jpg from the Akai media package to keyboard.jpg


Then run:

```sh
python akai_gui.py
```
to start the visual editor. 

### Usage

To load a preset click 'Get Presets from Keyboard'

Go to your keyboad global settings --> Sysex --> Send program

Pick the preset number you want to edit (do not use the 'All' option)
and push the enter knob to send the preset sysex dump to the editor.

Make your changes and then click the 'Send to Keyboard' button.

You can also save presets to your computer.

Done!



#### The actual interface
![screenshot](https://github.com/dobemad/MPK249/blob/main/gui-interface.png)

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

For midi support try edit port configurations in the mpk249_gui.py file
```sh
self.MIDI_IN_GET_NAME = "MIDIIN4 (MPK249)"
self.MIDI_OUT_SEND_NAME = "MIDIOUT4 (MPK249)"
```
with your actual midi port names for sysex communications. (e.g. "MIDIIN4 (MPK261)" - "MIDIOUT4 (MPK261)" )

## Command-line scripts usage
The command line scripts are my first attempt to configure the keyboard. You do not need those if you are using the visual editor.
I publish those if you are interested in developing your own tools or visual gui.
To use the command line scripts in the scripts folder, you will need to already have a SINGLE preset dump file (.syx)
(do not use the "ALL" preset dump).

All scripts have a --debug option so you read the actual dump bytes the script is reading / referring to

### Sample usage:
### Faders script

#### List values
```sh
python mpk2_fader_editor.py --import PRESET_FILE.syx --list-faders
```
Sample Output:

Fader  1 | Type=MIDI_CC    CC= 18 Ch= 0 Min=  0 Max=127 Din=Off

Fader  2 | Type=MIDI_CC    CC= 21 Ch= 0 Min=  0 Max=127 Din=Off

Fader  3 | Type=MIDI_CC    CC= 22 Ch= 0 Min=  0 Max=127 Din=Off

#### Set Values (set Fader 1 CC to 19)
```sh
python mpk2_fader_editor.py --import PRESET_FILE.syx  --set-fader 1 MIDI_CC 19 0 0 127 Off --export PRESET_FILE_NEW.syx
```
### Switches/Daw Buttons script
#### List values
```sh
python mpk2_switch_daw_editor.py --import PRESET_FILE.syx --list-switches
```
#### Set Values (set switch 1 channel to USBA1)
```sh
Python mpk2_switch_daw_editor.py --import PRESET_FILE.syx --set-switch 1 --type CC --channel USBA1 --export PRESET_FILE_NEW.syx
```
### Other scripts
see command line help

