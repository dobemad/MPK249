# File: mpk2_preset.py

# --- SEARCH TABLES ---
KNOB_OFFSET = 0x2FD; KNOB_SIZE = 9; KNOB_COUNT = 24
FADER_OFFSET = 0x3D5; FADER_SIZE = 6; FADER_COUNT = 24
PAD_OFFSET = 0x3D;  # FIXED
PAD_SIZE = 11; PAD_COUNT = 64
SWITCH_OFFSET = 0x465; SWITCH_COUNT = 24
DAW_OFFSET = 0x59D; DAW_COUNT = 5
CONTROL_SIZE = 13

channel_map = {"Common": 0, **{f"USBA{i}": i for i in range(1, 17)}, **{f"USBB{i}": 0x10 + i for i in range(1, 17)}}
channel_map_rev = {v: k for k, v in channel_map.items()}
note_map = {f"{name}{octave}": 12 * (octave + 1) + i for octave in range(-1, 10) for i, name in enumerate(["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])}
note_map_rev = {v: k for k, v in note_map.items()}
color_map = {0x00:"Off",0x01:"Red",0x02:"Orange",0x03:"Amber",0x04:"Yellow",0x05:"Green",0x06:"Green_Blue",0x07:"Aqua",0x08:"Light_Blue",0x09:"Blue",0x0A:"Purple",0x0B:"Pink",0x0C:"Hot_Pink",0x0D:"Pastel_Purple",0x0E:"Pastel_Green",0x0F:"Pastel_Pink",0x10:"Grey"}
color_map_rev = {v: k for k, v in color_map.items()}
key1_map = { 0x00:"1", 0x01:"2", 0x02:"3", 0x03:"4", 0x04:"5", 0x05:"6", 0x06:"7", 0x07:"8", 0x08:"9", 0x09:"0", 0x0A:"A", 0x0B:"B", 0x0C:"C", 0x0D:"D", 0x0E:"E", 0x0F:"F", 0x10:"G", 0x11:"H", 0x12:"I", 0x13:"J", 0x14:"K", 0x15:"L", 0x16:"M", 0x17:"N", 0x18:"O", 0x19:"P", 0x1A:"Q", 0x1B:"R", 0x1C:"S", 0x1D:"T", 0x1E:"U", 0x1F:"V", 0x20:"W", 0x21:"X", 0x22:"Y", 0x23:"Z", 0x24:"F1", 0x25:"F2", 0x26:"F3", 0x27:"F4", 0x28:"F5", 0x29:"F6", 0x2A:"F7", 0x2B:"F8", 0x2C:"F9", 0x2D:"F10", 0x2E:"F11", 0x2F:"F12", 0x30:"Backspace", 0x31:"Return", 0x32:"Up", 0x33:"Down", 0x34:"Left", 0x35:"Right", 0x36:"Tab", 0x37:",", 0x38:".", 0x39:"/", 0x3A:"[", 0x3B:"]", 0x3C:"\\", 0x3D:"'", 0x3E:";", 0x3F:"-", 0x40:"=", 0x41:"Esc", 0x42:"Insert", 0x43:"Home", 0x44:"Page Up", 0x45:"Delete", 0x46:"End", 0x47:"Page Down", 0x48:"Num 1", 0x49:"Num 2", 0x4A:"Num 3", 0x4B:"Num 4", 0x4C:"Num 5", 0x4D:"Num 6", 0x4E:"Num 7", 0x4F:"Num 8", 0x50:"Num 9", 0x51:"Num 0", 0x52:"(", 0x53:" " }
key1_map_rev = {v: k for k, v in key1_map.items()}
key2_map = { 0:"None", 1:"Control", 2:"Shift", 3:"Alt", 4:"Option", 5:"Control-Shift", 6:"Control-Alt", 7:"Control-Option", 8:"Shift-Alt", 9:"Shift-Option", 10:"Alt-Option", 11:"Control-Shift-Alt", 12:"Control-Option-Alt", 13:"Control-Shift-Option", 14:"Control-Shift-Alt-Option" }
key2_map_rev = {v: k for k, v in key2_map.items()}
daw_names = ["Enter", "Left", "Right", "Up", "Down"]

class MPK2Preset:
    def __init__(self, sysex_filepath=None, data=None):
        self.sysex_data = None
        if sysex_filepath: self.load_from_file(sysex_filepath)
        elif data: self.load_from_data(data)

    def load_from_data(self, data):
        self.sysex_data = bytearray(data)

    def load_from_file(self, filepath):
        try:
            with open(filepath, 'rb') as f: self.load_from_data(f.read())
        except Exception: self.sysex_data = None
            
    def save_to_file(self, filepath):
        if not self.sysex_data: return
        try:
            with open(filepath, 'wb') as f: f.write(self.sysex_data)
        except Exception as e: print(f"Errore durante il salvataggio: {e}")

    # --- METADATA (Offset) ---
    def get_model(self):
        if not self.sysex_data or len(self.sysex_data) <= 3: return "N/A"
        return {0x24:"MPK249", 0x25:"MPK261", 0x23:"MPK225"}.get(self.sysex_data[3], "Unknown")

    def get_preset_number(self):
        if not self.sysex_data or len(self.sysex_data) <= 7: return -1
        return self.sysex_data[7]

    def set_preset_number(self, number):
        if not self.sysex_data or len(self.sysex_data) <= 7: return
        if 0 <= number <= 29:
            self.sysex_data[7] = number

    def get_preset_name(self):
        if not self.sysex_data or len(self.sysex_data) <= 15: return ""
        # Legge 8 byte e rimuove gli spazi finali
        return self.sysex_data[8:16].decode('ascii', errors='ignore').rstrip(' ')

    def set_preset_name(self, name):
        if not self.sysex_data or len(self.sysex_data) <= 15: return
        # Prepara una stringa di 8 byte, riempiendo con spazi (' ')
        padded_name = name.encode('ascii', errors='ignore').ljust(8, b' ')[:8]
        self.sysex_data[8:16] = padded_name

    # --- CONTROLS  ---
    def get_knob(self, index):
        if not self.sysex_data: return {}
        offset = KNOB_OFFSET + (index - 1) * KNOB_SIZE
        block = self.sysex_data[offset:offset+KNOB_SIZE]
        type_map = {0x00: "MIDI_CC", 0x01: "AFTERTOUCH", 0x02: "INC_DEC1", 0x03: "INC_DEC2"}
        return { "type": type_map.get(block[0]), "channel": channel_map_rev.get(block[1]), "cc": block[2], "min": block[3], "max": block[4], "midi_to_din": "On" if block[5] == 1 else "Off", "msb": block[6], "lsb": block[7], "value": block[8] }

    def set_knob(self, index, **kwargs):
        if not self.sysex_data: return
        offset = KNOB_OFFSET + (index - 1) * KNOB_SIZE; block = self.sysex_data[offset:offset+KNOB_SIZE]
        type_map = {"MIDI_CC": 0x00, "AFTERTOUCH": 0x01, "INC_DEC1": 0x02, "INC_DEC2": 0x03}
        for k, v in kwargs.items():
            if k == "type": block[0] = type_map.get(str(v).upper(), block[0])
            elif k == "channel": block[1] = channel_map.get(v, block[1])
            elif k == "cc": block[2] = int(v)
            elif k == "min": block[3] = int(v)
            elif k == "max": block[4] = int(v)
            elif k == "midi_to_din": block[5] = 1 if str(v).upper() == "ON" else 0
            elif k == "msb": block[6] = int(v)
            elif k == "lsb": block[7] = int(v)
            elif k == "value": block[8] = int(v)
        self.sysex_data[offset:offset+KNOB_SIZE] = block
        
    def get_fader(self, index):
        if not self.sysex_data: return {}
        offset = FADER_OFFSET + (index - 1) * FADER_SIZE
        block = self.sysex_data[offset:offset+FADER_SIZE]
        return { "type": "AFTERTOUCH" if block[0] == 0x01 else "MIDI_CC", "channel": channel_map_rev.get(block[1]), "cc": block[2], "min": block[3], "max": block[4], "midi_to_din": "On" if block[5] == 1 else "Off" }

    def set_fader(self, index, **kwargs):
        if not self.sysex_data: return
        offset = FADER_OFFSET + (index - 1) * FADER_SIZE; block = self.sysex_data[offset:offset+FADER_SIZE]
        for k, v in kwargs.items():
            if k == "type": block[0] = 0x01 if str(v).upper() == "AFTERTOUCH" else 0x00
            elif k == "channel": block[1] = channel_map.get(v, block[1])
            elif k == "cc": block[2] = int(v)
            elif k == "min": block[3] = int(v)
            elif k == "max": block[4] = int(v)
            elif k == "midi_to_din": block[5] = 1 if str(v).upper() == "ON" else 0
        self.sysex_data[offset:offset+FADER_SIZE] = block

    def get_pad(self, index):
        if not self.sysex_data: return {}
        offset = PAD_OFFSET + (index - 1) * PAD_SIZE
        block = self.sysex_data[offset:offset+PAD_SIZE]
        type_raw = block[0]
        d = {"channel": channel_map_rev.get(block[1]), "midi_to_din": "On" if block[3] == 1 else "Off", "mode": "Toggle" if block[4] == 1 else "Momentary", "aftertouch": {0:"Off", 1:"Channel", 2:"Poly"}.get(block[5]), "off_color": color_map.get(block[9]), "on_color": color_map.get(block[10])}
        if type_raw == 1: d.update({"type": "ProgramChange", "program": block[2]})
        elif type_raw == 2: d.update({"type": "ProgramBank", "program": block[6], "msb": block[7], "lsb": block[8]})
        else: d.update({"type": "Note", "note": note_map_rev.get(block[2])})
        return d
        
    def set_pad(self, index, **kwargs):
        if not self.sysex_data: return
        offset = PAD_OFFSET + (index - 1) * PAD_SIZE; block = self.sysex_data[offset:offset+PAD_SIZE]
        type_map = {"NOTE": 0, "PROGRAMCHANGE": 1, "PROGRAMBANK": 2}
        if "type" in kwargs: block[0] = type_map.get(str(kwargs["type"]).upper(), block[0])
        for k, v in kwargs.items():
            if k == "channel": block[1] = channel_map[v]
            elif k == "midi_to_din": block[3] = 1 if str(v).upper() == "ON" else 0
            elif k == "mode": block[4] = 1 if str(v).upper() == "TOGGLE" else 0
            elif k == "aftertouch": block[5] = {"OFF":0, "CHANNEL":1, "POLY":2}.get(str(v).upper(), block[5])
            elif k == "off_color": block[9] = color_map_rev[v]
            elif k == "on_color": block[10] = color_map_rev[v]
            if block[0] == 0 and k == "note": block[2] = note_map[v]
            elif block[0] == 1 and k == "program": block[2] = int(v)
            elif block[0] == 2:
                if k == "program": block[6] = int(v)
                elif k == "msb": block[7] = int(v)
                elif k == "lsb": block[8] = int(v)
        self.sysex_data[offset:offset+PAD_SIZE] = block
        
    def _get_control(self, base_offset, index):
        if not self.sysex_data: return {}
        offset = base_offset + (index - 1) * CONTROL_SIZE
        block = self.sysex_data[offset:offset + CONTROL_SIZE]
        d = {}; type_raw = block[0]
        d['channel'] = channel_map_rev.get(block[1], block[1])
        d['mode'] = "Toggle" if block[3] == 1 else "Momentary"
        if type_raw in [0, 1, 2, 3]: d['midi_to_din'] = "On" if block[7] == 1 else "Off"

        if type_raw == 0: d.update({"type": "CC", "cc": block[2], "invert": "On" if block[5] == 1 else "Off"})
        elif type_raw == 1: d.update({"type": "Note", "note": note_map_rev.get(block[8], block[8]), "velocity": block[9]})
        elif type_raw == 2: d.update({"type": "ProgChange", "program": block[2]})
        elif type_raw == 3: d.update({"type": "ProgBank", "program": block[4], "msb": block[5], "lsb": block[6]})
        elif type_raw == 4: d.update({"type": "Keystroke", "key1": key1_map.get(block[11]), "key2": key2_map.get(block[12])})
        else: d['type'] = f"UNKNOWN_{type_raw}"
        return d

    def _write_control(self, base_offset, index, **kwargs):
        if not self.sysex_data: return
        offset = base_offset + (index - 1) * CONTROL_SIZE; block = self.sysex_data[offset:offset+CONTROL_SIZE]
        type_map = {"NOTE": 1, "CC": 0, "PROGCHANGE": 2, "PROGBANK": 3, "KEYSTROKE": 4}
        if "type" in kwargs:
            new_type_val = type_map.get(str(kwargs["type"]).upper())
            if new_type_val is not None: block[0] = new_type_val
        current_type = block[0]

        for k, v in kwargs.items():
            if k == "channel": block[1] = channel_map.get(v, block[1])
            elif k == "mode": block[3] = 1 if str(v).upper() == "TOGGLE" else 0
            if current_type in [0,1,2,3] and k == "midi_to_din": block[7] = 1 if str(v).upper() == "ON" else 0
            
            if current_type == 0:
                if k == "cc": block[2] = int(v)
                elif k == "invert": block[5] = 1 if str(v).upper() == "ON" else 0
            elif current_type == 1:
                if k == "note": block[8] = note_map.get(v, block[8])
                elif k == "velocity": block[9] = int(v)
            elif current_type == 2:
                if k == "program": block[2] = int(v)
            elif current_type == 3:
                if k == "program": block[4] = int(v)
                elif k == "msb": block[5] = int(v)
                elif k == "lsb": block[6] = int(v)
            elif current_type == 4:
                if k == "key1": block[11] = key1_map_rev.get(v, block[11])
                elif k == "key2": block[12] = key2_map_rev.get(v, block[12])
        self.sysex_data[offset:offset+CONTROL_SIZE] = block
        
    def get_switch(self, index): return self._get_control(SWITCH_OFFSET, index)
    def set_switch(self, index, **kwargs): self._write_control(SWITCH_OFFSET, index, **kwargs)
    def get_daw(self, name): return self._get_control(DAW_OFFSET, daw_names.index(name) + 1)
    def set_daw(self, name, **kwargs): self._write_control(DAW_OFFSET, daw_names.index(name) + 1, **kwargs)
