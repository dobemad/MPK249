# A visual editor for Akai MPK2 series + a collection of command line scripts
Tested and reversed engineered on Akai MPK249. 
Usage on other controllers of the MPK2 series is _untested_.
The /scripts are a collection of command line tools for reading / writing single preset dump files and are mostly for research purpose. 
End user should use the gui only

_Disclaimer:_ Use of this material can possibly void your warranty, corrupt your presets or brick your controller.

## Downloads

If you are not familiar with setting up a python environment you can download the MPK249 version for both Windows and Mac. 

you can download the Windows executable from this repository [here](https://github.com/dobemad/MPK249/releases/download/v1.0.0/mpk249_gui.exe).

NEW! you can download the OSx dmg from this repository [here](https://github.com/dobemad/MPK249/releases/download/V1.1.0mac/MPK249_Visual_Editor.dmg).

That's all you have to do to use the app hopefully. 

### Pre-requisites for running the GUI via source code:

Intall python. OSX users: install python via brew, as it contains a working version of customtkinter library

Then install these dependencies:

```sh
pip install customtkinter pillow python-rtmidi
```

Download Akai media images (for the gui)

https://cdn.inmusicbrands.com/akai/attachments/MPK249/MPK249%20-%20Media.zip

And extract MPK249_ortho_10x8_media_01.jpg

NB: On Mac you will have to ~~crop and resize the image to 1058x635~~ use [this file](https://github.com/dobemad/MPK249/blob/main/keyboard.jpg) as it is.


### Works that made this possible:
These guys are the real heroes:

https://github.com/nsmith-/mpk2

http://practicalusage.com/akai-mpk261-mpk2-series-controlling-the-controller-with-sysex/

http://practicalusage.com/akai-mpk261-one-more-thing/

https://cdn.inmusicbrands.com/akai/attachments/MPK249/MPK2_Series_Bitwig_Scripts_v1.0.8.zip

## Running the GUI in python

Place these 3 files in the same directory

mpk249_gui.py (NB: download mpk249_gui_mac.py and rename it to mpk249_gui.py if you are on Mac)

mpk2_preset.py

Renamed MPK249_ortho_10x8_media_01.jpg from the Akai media package to keyboard.jpg ~~(crop and resize the image to 1058x635 if you are on Mac)~~
MAC USERS: use [this file](https://github.com/dobemad/MPK249/blob/main/keyboard.jpg) as it is

Then run:

```sh
python mpk249_gui.py
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

The script is set to identify the keyboard from the sysex data. 

```sh
def get_model(self):
        if not self.sysex_data or len(self.sysex_data) <= 3: return "N/A"
        return {0x24:"MPK249", 0x25:"MPK261", 0x23:"MPK225"}.get(self.sysex_data[3], "Unknown")
```

For midi support edit the port configurations in the mpk249_gui.py file
```sh
self.MIDI_IN_GET_NAME = "MIDIIN4 (MPK249)"
self.MIDI_OUT_SEND_NAME = "MIDIOUT4 (MPK249)"
```
with your actual midi port names for sysex communications. (e.g. "MIDIIN4 (MPK261)" - "MIDIOUT4 (MPK261)" ) on windows

On mac now should work out of the box with autofinding model and portname.



## Command-line scripts usage
The command line scripts are my first attempt to configure the keyboard. You don't need them if you are using the visual editor.
I published those if you are interested in developing your own tools or visual gui.
To use the command line scripts in the scripts folder, you will need to already have a SINGLE preset dump file (.syx)
(do not use the "ALL" preset dump).

All scripts have a --debug option so you can read the actual dump bytes that the script is reading / referring to

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

