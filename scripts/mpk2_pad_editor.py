#!/usr/bin/env python3
import argparse
import mido

# --- Constants ---
PAD_OFFSET = 0x3C
PAD_SIZE = 11
PAD_COUNT = 64

# --- Lookup tables (unchanged) ---
channel_map = {"Common": 0}
channel_map.update({f"USBA{i}": i for i in range(1, 17)})
channel_map.update({f"USBB{i}": 0x10 + i for i in range(1, 17)})
channel_map_rev = {v: k for k, v in channel_map.items()}

note_map = {}
for octave in range(-1, 10):
    for i, name in enumerate(["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]):
        note = 12 * (octave + 1) + i
        note_map[f"{name}{octave}"] = note
note_map_rev = {v: k for k, v in note_map.items()}

color_map = {
    0x00:"Off", 0x01:"Red", 0x02:"Orange", 0x03:"Amber", 0x04:"Yellow", 0x05:"Green",
    0x06:"Green_Blue", 0x07:"Aqua", 0x08:"Light_Blue", 0x09:"Blue", 0x0A:"Purple",
    0x0B:"Pink", 0x0C:"Hot_Pink", 0x0D:"Pastel_Purple", 0x0E:"Pastel_Green",
    0x0F:"Pastel_Pink", 0x10:"Grey"
}
color_map_rev = {v: k for k, v in color_map.items()}

# --- Pad helpers ---
def get_pad_block(data, pad_index):
    base = PAD_OFFSET + (pad_index - 1) * PAD_SIZE
    return list(data[base:base + PAD_SIZE])

def set_pad_block(data, pad_index, block):
    base = PAD_OFFSET + (pad_index - 1) * PAD_SIZE
    data[base:base + PAD_SIZE] = block

def parse_pad(block):
    d = {}
    pad_type = block[0]

    # Parse all values based on the final correct mapping
    d['channel'] = channel_map_rev.get(block[1], block[1])
    d['midi_to_din'] = "On" if block[3] == 1 else "Off"
    d['mode'] = "Toggle" if block[4] == 1 else "Momentary"
    d['aftertouch'] = {0:"Off", 1:"Channel", 2:"Poly"}.get(block[5], block[5])
    d['off_color'] = color_map.get(block[9], block[9])
    d['on_color'] = color_map.get(block[10], block[10])

    if pad_type == 0x01: # Program Change
        d['type'] = "ProgramChange"
        d['program'] = block[2]
    elif pad_type == 0x02: # Program Bank
        d['type'] = "ProgramBank"
        d['program'] = block[6]
        d['msb'] = block[7]
        d['lsb'] = block[8]
    else: # Note
        d['type'] = "Note"
        d['note'] = note_map_rev.get(block[2], block[2])
        
    d['raw_bytes'] = ' '.join(f'{b:02X}' for b in block)
    return d

def edit_pad(block, args):
    if args.type:
        block[0] = {"Note": 0x00, "ProgramChange": 0x01, "ProgramBank": 0x02}[args.type]

    if args.channel: block[1] = channel_map[args.channel]
    if args.midi_to_din: block[3] = 1 if args.midi_to_din == "On" else 0
    if args.mode: block[4] = 1 if args.mode == "Toggle" else 0
    if args.aftertouch: block[5] = {"Off":0, "Channel":1, "Poly":2}[args.aftertouch]
    if args.off_color: block[9] = color_map_rev[args.off_color]
    if args.on_color: block[10] = color_map_rev[args.on_color]

    current_type = block[0]
    if current_type == 0x00 and args.note:
        block[2] = note_map[args.note]
    elif current_type == 0x01 and args.program is not None:
        block[2] = args.program
    elif current_type == 0x02:
        if args.program is not None: block[6] = args.program
        if args.msb is not None: block[7] = args.msb
        if args.lsb is not None: block[8] = args.lsb
        
    return block

def main():
    parser = argparse.ArgumentParser(description="MPK2 Pad Editor")
    parser.add_argument("--import", dest="import_file", required=True, help="Input .syx file")
    parser.add_argument("--export", dest="export_file", help="Output .syx file")
    parser.add_argument("--list-pads", action="store_true", help="List all 64 pads")
    parser.add_argument("--get-pad", type=int, help="Show pad details for pad index (1-64)")
    parser.add_argument("--set-pad", type=int, help="Modify pad index (1-64)")
    parser.add_argument("--debug", action="store_true", help="Show raw byte values for pads")
    
    parser.add_argument("--type", choices=["Note", "ProgramChange", "ProgramBank"], help="Set the pad's function")
    parser.add_argument("--channel", choices=channel_map.keys(), help="Set MIDI channel")
    parser.add_argument("--note", choices=note_map.keys(), help="Set Note (for Type=Note)")
    parser.add_argument("--mode", choices=["Momentary", "Toggle"], help="Set pad mode")
    parser.add_argument("--midi-to-din", choices=["On", "Off"], help="Set MIDI to DIN output")
    parser.add_argument("--aftertouch", choices=["Off", "Channel", "Poly"], help="Set aftertouch")
    parser.add_argument("--program", type=int, help="Set Program Number")
    parser.add_argument("--msb", type=int, help="Set Program Bank MSB")
    parser.add_argument("--lsb", type=int, help="Set Program Bank LSB")
    parser.add_argument("--off-color", dest="off_color", choices=color_map.values())
    parser.add_argument("--on-color", dest="on_color", choices=color_map.values())

    args = parser.parse_args()

    try:
        msgs = mido.read_syx_file(args.import_file)
        payload = list(msgs[0].data)
    except (FileNotFoundError, IndexError):
        print(f"Error: Could not read SysEx file from {args.import_file}")
        return

    def print_pad_details(pad_index, pad_data):
        raw_bytes = pad_data.pop('raw_bytes')
        print(f"Pad {pad_index:2d}: {pad_data}", end='')
        if args.debug:
            print(f" | Raw: [ {raw_bytes} ]")
        else:
            print()

    if args.list_pads:
        for i in range(1, PAD_COUNT + 1):
            print_pad_details(i, parse_pad(get_pad_block(payload, i)))
    
    if args.get_pad:
        print_pad_details(args.get_pad, parse_pad(get_pad_block(payload, args.get_pad)))

    if args.set_pad:
        block = get_pad_block(payload, args.set_pad)
        modified_block = edit_pad(block, args)
        set_pad_block(payload, args.set_pad, modified_block)
        print("Modified Pad -> ", end='')
        print_pad_details(args.set_pad, parse_pad(modified_block))

    if args.export_file:
        mido.write_syx_file(args.export_file, [mido.Message('sysex', data=payload)])
        print(f"Exported to {args.export_file}")

if __name__ == "__main__":
    main()