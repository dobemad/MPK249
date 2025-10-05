#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import mido

# --- Constants for All Controls ---
SWITCH_OFFSET = 0x465
SWITCH_COUNT = 24
DAW_OFFSET = 0x59D  # Starts immediately after the 24 switches
DAW_COUNT = 5
CONTROL_SIZE = 13   # Using the same 13-byte structure

# --- Lookup Tables ---
channel_map = {"Common": 0, **{f"USBA{i}": i for i in range(1, 17)}, **{f"USBB{i}": 0x10 + i for i in range(1, 17)}}
channel_map_rev = {v: k for k, v in channel_map.items()}

note_map = {f"{name}{octave}": 12 * (octave + 1) + i for octave in range(-1, 10) for i, name in enumerate(["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])}
note_map_rev = {v: k for k, v in note_map.items()}

# This map includes some verified and some guessed keys
key1_map = {
    0x00:"1", 0x01:"2", 0x02:"3", 0x03:"4", 0x04:"5", 0x05:"6", 0x06:"7", 0x07:"8", 0x08:"9", 0x09:"0", 0x0A:"A", 0x0B:"B", 0x0C:"C",
    0x0D:"D", 0x0E:"E", 0x0F:"F", 0x10:"G", 0x11:"H", 0x12:"I", 0x13:"J", 0x14:"K", 0x15:"L", 0x16:"M", 0x17:"N", 0x18:"O", 0x19:"P",
    0x1A:"Q", 0x1B:"R", 0x1C:"S", 0x1D:"T", 0x1E:"U", 0x1F:"V", 0x20:"W", 0x21:"X", 0x22:"Y", 0x23:"Z", 0x24:"F1", 0x25:"F2", 0x26:"F3",
    0x27:"F4", 0x28:"F5", 0x29:"F6", 0x2A:"F7", 0x2B:"F8", 0x2C:"F9", 0x2D:"F10", 0x2E:"F11", 0x2F:"F12", 0x30:"Backspace",
    0x31:"Return", 0x32:"Up", 0x33:"Down", 0x34:"Left", 0x35:"Right", 0x36:"Tab", 0x37:",", 0x38:".", 0x39:"/", 0x3A:"[", 0x3B:"]",
    # ------------------------------------
    0x3C:"\\", 0x3D:"'", 0x3E:";", 0x3F:"-", 0x40:"=", 0x41:"Esc", 0x42:"Insert", 0x43:"Home", 0x44:"Page Up", 0x45:"Delete",
    0x46:"End", 0x47:"Page Down", 0x48:"Num 1", 0x49:"Num 2", 0x4A:"Num 3", 0x4B:"Num 4", 0x4C:"Num 5", 0x4D:"Num 6", 0x4E:"Num 7",
    0x4F:"Num 8", 0x50:"Num 9", 0x51:"Num 0", 0x52:"(", 0x53:" "
}
key1_map_rev = {v: k for k, v in key1_map.items()}

key2_map = {
    0:"None", 1:"Control", 2:"Shift", 3:"Alt", 4:"Option", 5:"Control-Shift", 6:"Control-Alt", 7:"Control-Option", 8:"Shift-Alt",
    9:"Shift-Option", 10:"Alt-Option", 11:"Control-Shift-Alt", 12:"Control-Option-Alt", 13:"Control-Shift-Option", 14:"Control-Shift-Alt-Option"
}
key2_map_rev = {v: k for k, v in key2_map.items()}

daw_map = {"Enter": 0, "Left": 1, "Right": 2, "Up": 3, "Down": 4}
daw_names = ["Enter", "Left", "Right", "Up", "Down"]

def load_sysex(path):
    with open(path, "rb") as f: return bytearray(f.read())

def save_sysex(path, data):
    with open(path, "wb") as f: f.write(data)

def parse_control(data, base_offset, index):
    offset = base_offset + index * CONTROL_SIZE
    block = data[offset:offset + CONTROL_SIZE]
    d = {}
    type_raw = block[0]
    
    d['channel'] = channel_map_rev.get(block[1], block[1])
    d['mode'] = "Toggle" if block[3] == 1 else "Momentary"

    if type_raw in [0, 1, 2, 3]:
        d['midi_to_din'] = "On" if block[7] == 1 else "Off"

    if type_raw == 0:
        d['type'] = "CC"; d['cc'] = block[2]; d['invert'] = "On" if block[5] == 1 else "Off"
    elif type_raw == 1:
        d['type'] = "Note"; d['note'] = note_map_rev.get(block[8], block[8]); d['velocity'] = block[9]
    elif type_raw == 2:
        d['type'] = "ProgChange"; d['program'] = block[2]
    elif type_raw == 3:
        d['type'] = "ProgBank"; d['program'] = block[4]; d['msb'] = block[5]; d['lsb'] = block[6]
    elif type_raw == 4:
        d['type'] = "Keystroke"; d['key1'] = key1_map.get(block[11], f"Raw:{block[11]}"); d['key2'] = key2_map.get(block[12], f"Raw:{block[12]}")
    else: d['type'] = f"UNKNOWN_{type_raw}"
        
    d['raw_bytes'] = ' '.join(f'{b:02X}' for b in block)
    return d

def write_control(data, base_offset, index, args):
    offset = base_offset + index * CONTROL_SIZE
    block = bytearray(data[offset:offset + CONTROL_SIZE])
    
    if args.channel: block[1] = channel_map[args.channel]
    if args.mode: block[3] = 1 if args.mode.upper() == "TOGGLE" else 0
    
    type_upper = args.type.upper()

    if args.midi_to_din and type_upper in ["CC", "NOTE", "PROGCHANGE", "PROGBANK"]:
        block[7] = 1 if args.midi_to_din.upper() == "ON" else 0

    if type_upper == "CC":
        block[0] = 0;
        if args.number is not None: block[2] = args.number
        if args.invert: block[5] = 1 if args.invert.upper() == "ON" else 0
    elif type_upper == "NOTE":
        block[0] = 1
        if args.note: block[8] = note_map[args.note]
        if args.velocity is not None: block[9] = args.velocity
    elif type_upper == "PROGCHANGE":
        block[0] = 2;
        if args.number is not None: block[2] = args.number
    elif type_upper == "PROGBANK":
        block[0] = 3
        if args.number is not None: block[4] = args.number
        if args.msb is not None: block[5] = args.msb
        if args.lsb is not None: block[6] = args.lsb
    elif type_upper == "KEYSTROKE":
        block[0] = 4
        if args.key1: block[11] = key1_map_rev.get(args.key1, 0)
        if args.key2: block[12] = key2_map_rev.get(args.key2, 0)
        
    data[offset:offset + CONTROL_SIZE] = block
    return data

def main():
    parser = argparse.ArgumentParser(description="MPK2 Switch & DAW Editor")
    parser.add_argument("--import", dest="infile", required=True); parser.add_argument("--export", dest="outfile")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--list-switches", action="store_true"); parser.add_argument("--set-switch", type=int, metavar="INDEX")
    parser.add_argument("--list-daw", action="store_true"); parser.add_argument("--set-daw", choices=daw_map.keys(), metavar="NAME")
    
    parser.add_argument("--type", choices=["Note", "CC", "ProgChange", "ProgBank", "Keystroke"])
    parser.add_argument("--note", choices=note_map.keys()); parser.add_argument("--number", type=int, help="CC/Program Number")
    parser.add_argument("--channel", choices=channel_map.keys()); parser.add_argument("--mode", choices=["Momentary", "Toggle"])
    parser.add_argument("--midi-to-din", choices=["On", "Off"]); parser.add_argument("--invert", choices=["On", "Off"])
    parser.add_argument("--velocity", type=int); parser.add_argument("--msb", type=int); parser.add_argument("--lsb", type=int)
    parser.add_argument("--key1", choices=key1_map_rev.keys()); parser.add_argument("--key2", choices=key2_map_rev.keys())
    
    args = parser.parse_args()
    data = load_sysex(args.infile)
    
    def print_details(label, control_data):
        raw = control_data.pop('raw_bytes')
        print(f"{label:<12}: {control_data}", end='');
        if args.debug: print(f" | Raw: [ {raw} ]")
        else: print()
        
    if args.list_switches:
        for i in range(SWITCH_COUNT):
            print_details(f"Switch {i+1:2d}", parse_control(data, SWITCH_OFFSET, i))
            
    if args.list_daw:
        for i in range(DAW_COUNT):
            print_details(f"DAW {daw_names[i]}", parse_control(data, DAW_OFFSET, i))
            
    if args.set_switch or args.set_daw:
        if not args.type:
            print("Error: --type is required when setting a control."); return
        
        if args.set_switch:
            index = args.set_switch - 1
            offset = SWITCH_OFFSET
            label = f"Switch {args.set_switch}"
        else:
            index = daw_map[args.set_daw]
            offset = DAW_OFFSET
            label = f"DAW {args.set_daw}"

        data = write_control(data, offset, index, args)
        print("Modified -> ", end=''); print_details(label, parse_control(data, offset, index))

    if args.outfile:
        save_sysex(args.outfile, data)
        print(f"Data saved to {args.outfile}")

if __name__ == "__main__":
    main()