#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

# --- Constants for Faders ---
FADER_OFFSET = 0x3D5   # HYPOTHESIS: Starts immediately after the 24 knobs.
FADER_SIZE = 6         # CORRECTED: Each fader's data is 6 bytes long.
FADER_COUNT = 24       # 3 banks of 8 faders

def load_sysex(path):
    with open(path, "rb") as f:
        return bytearray(f.read())

def save_sysex(path, data):
    with open(path, "wb") as f:
        f.write(data)

def parse_fader(data, index):
    """Parses a 6-byte fader block based on the new, correct model."""
    offset = FADER_OFFSET + index * FADER_SIZE
    block = data[offset:offset+FADER_SIZE]

    # Hypothesized mapping for the 6 bytes
    type_raw = block[0]
    fader_type = "AFTERTOUCH" if type_raw == 0x01 else "MIDI_CC"

    return {
        "index": index + 1,
        "type": fader_type,
        "channel": block[1],
        "cc": block[2],
        "min": block[3],
        "max": block[4],
        "midi_to_din": "On" if block[5] == 1 else "Off",
        "raw_bytes": ' '.join(f'{b:02X}' for b in block)
    }

def write_fader(data, index, fader_type, cc, channel, minv, maxv, midi_to_din_str):
    """Writes a 6-byte fader block."""
    offset = FADER_OFFSET + index * FADER_SIZE
    block = bytearray(data[offset:offset+FADER_SIZE])
    
    block[0] = 0x01 if fader_type.upper() == "AFTERTOUCH" else 0x00
    block[1] = channel
    block[2] = cc
    block[3] = minv
    block[4] = maxv
    block[5] = 1 if midi_to_din_str.upper() == "ON" else 0

    data[offset:offset+FADER_SIZE] = block
    return data

def main():
    parser = argparse.ArgumentParser(description="MPK2 Fader Editor (6-Byte Model)")
    parser.add_argument("--import", dest="infile", required=True, help="Input syx file")
    parser.add_argument("--export", dest="outfile", help="Output syx file")
    parser.add_argument("--debug", action="store_true", help="Show raw byte values for verification")

    parser.add_argument("--list-faders", action="store_true", help="List all 24 faders")
    parser.add_argument("--set-fader", nargs=7, metavar=("INDEX", "TYPE", "CC", "CH", "MIN", "MAX", "DIN"),
                        help="Set fader values (TYPE=MIDI_CC|AFTERTOUCH, DIN=On|Off)")

    args = parser.parse_args()
    data = load_sysex(args.infile)

    if args.list_faders:
        for i in range(FADER_COUNT):
            fader_data = parse_fader(data, i)
            raw_bytes = fader_data.pop('raw_bytes')
            print(f"Fader {fader_data['index']:2d} | Type={fader_data['type']:10s} CC={fader_data['cc']:3d} Ch={fader_data['channel']:2d} "
                  f"Min={fader_data['min']:3d} Max={fader_data['max']:3d} Din={fader_data['midi_to_din']:3s}", end='')
            if args.debug:
                print(f" | Raw: [ {raw_bytes} ]")
            else:
                print()

    if args.set_fader:
        idx, ftype, cc, ch, minv, maxv, din = [int(v) if v.isdigit() else v for v in args.set_fader]
        data = write_fader(data, idx - 1, ftype, cc, ch, minv, maxv, din)
        print(f"Fader {idx} updated. Save with --export.")

    if args.outfile:
        save_sysex(args.outfile, data)
        print(f"Data saved to {args.outfile}")
if __name__ == "__main__":
    main()
