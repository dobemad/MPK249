#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

# Constants
KNOB_OFFSET = 0x2FD
KNOB_SIZE = 9
KNOB_COUNT = 24

def parse_knob(data, index):
    """Reads and interprets the 9 bytes of a single knob with mapping."""
    offset = KNOB_OFFSET + index * KNOB_SIZE
    block = data[offset:offset+KNOB_SIZE]

    # Final, complete byte mapping
    type_raw = block[0]
    channel = block[1]
    cc = block[2]
    minv = block[3]
    maxv = block[4]
    midi_to_din = "On" if block[5] == 1 else "Off"
    msb = block[6]
    lsb = block[7]
    value = block[8]

    if type_raw == 0x00:
        knob_type = "MIDI_CC"
    elif type_raw == 0x01:
        knob_type = "AFTERTOUCH"
    elif type_raw == 0x02:
        knob_type = "INC_DEC1"
    elif type_raw == 0x03:
        knob_type = "INC_DEC2"
    else:
        knob_type = f"UNKNOWN_0x{type_raw:02X}"

    return {
        "index": index + 1,
        "type": knob_type,
        "cc": cc,
        "channel": channel,
        "min": minv,
        "max": maxv,
        "midi_to_din": midi_to_din,
        "msb": msb,
        "lsb": lsb,
        "value": value,
        "raw_bytes": ' '.join(f'{b:02X}' for b in block)
    }

def write_knob(data, index, knob_type, cc, channel, minv, maxv, msb=0, lsb=0, midi_to_din_str="Off", value=0):
    """Writes a knob's data into the sysex byte array with the final mapping."""
    offset = KNOB_OFFSET + index * KNOB_SIZE
    block = bytearray(data[offset:offset+KNOB_SIZE])

    # Map all parameters to their correct byte positions
    block[1] = channel
    block[2] = cc
    block[3] = minv
    block[4] = maxv
    block[5] = 1 if midi_to_din_str.upper() == "ON" else 0
    block[6] = msb
    block[7] = lsb
    block[8] = value

    if knob_type == "MIDI_CC":
        block[0] = 0x00
        # For non-INC/DEC types, MSB/LSB/Value are typically 0
        block[6], block[7], block[8] = 0, 0, 0
    elif knob_type == "AFTERTOUCH":
        block[0] = 0x01
        block[6], block[7], block[8] = 0, 0, 0
    elif knob_type == "INC_DEC1":
        block[0] = 0x02
    elif knob_type == "INC_DEC2":
        block[0] = 0x03

    data[offset:offset+KNOB_SIZE] = block
    return data

def load_sysex(path):
    with open(path, "rb") as f:
        return bytearray(f.read())

def save_sysex(path, data):
    with open(path, "wb") as f:
        f.write(data)

def main():
    parser = argparse.ArgumentParser(description="MPK2 Knob Editor")
    parser.add_argument("--import", dest="infile", required=True, help="Input syx file")
    parser.add_argument("--export", dest="outfile", help="Output syx file")
    parser.add_argument("--list-knobs", action="store_true", help="List all knobs")
    parser.add_argument("--set-knob", nargs=10, 
                        metavar=("INDEX", "TYPE", "CC", "CH", "MIN", "MAX", "MSB", "LSB", "DIN", "VALUE"),
                        help="Set knob values (DIN=On|Off, VALUE=0-127)")
    parser.add_argument("--debug", action="store_true", help="Show raw byte values for knobs")
    
    args = parser.parse_args()

    data = load_sysex(args.infile)

    def print_knob_details(knob_data):
        raw_bytes = knob_data.pop('raw_bytes')
        print(f"Knob {knob_data['index']:2d} | Type={knob_data['type']:10s} CC={knob_data['cc']:3d} Ch={knob_data['channel']:2d} "
              f"Min={knob_data['min']:3d} Max={knob_data['max']:3d} MSB={knob_data['msb']:3d} LSB={knob_data['lsb']:3d} "
              f"Din={knob_data['midi_to_din']:3s} Val={knob_data['value']:3d}", end='')
        if args.debug:
            print(f" | Raw: [ {raw_bytes} ]")
        else:
            print()

    if args.list_knobs:
        for i in range(KNOB_COUNT):
            print_knob_details(parse_knob(data, i))

    if args.set_knob:
        idx = int(args.set_knob[0]) - 1
        ktype = args.set_knob[1].upper()
        cc = int(args.set_knob[2])
        ch = int(args.set_knob[3])
        minv = int(args.set_knob[4])
        maxv = int(args.set_knob[5])
        msb = int(args.set_knob[6])
        lsb = int(args.set_knob[7])
        din = args.set_knob[8]
        val = int(args.set_knob[9])
        data = write_knob(data, idx, ktype, cc, ch, minv, maxv, msb, lsb, din, val)
        
        print("Modified Knob -> ", end='')
        print_knob_details(parse_knob(data, idx))

        if args.outfile:
            save_sysex(args.outfile, data)
            print(f"\nKnob {idx+1} updated and saved to {args.outfile}")
        else:
            print("\nNo output file specified, changes not saved.")

if __name__ == "__main__":
    main()