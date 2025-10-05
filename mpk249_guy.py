# File: mpk249_gui.py
import customtkinter as ctk
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import rtmidi
import threading
import time
import re # Import regex module
# Make sure the mpk2_preset.py file is in the same folder
from mpk2_preset import MPK2Preset, note_map, color_map, channel_map, key1_map_rev, key2_map_rev, daw_names, note_map_rev

# --- Bank Cloner Window ---
class BankClonerWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.parent = parent
        self.title("Bank Cloner")
        self.geometry("350x250")

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Control Type:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Pads")
        self.type_menu = ctk.CTkOptionMenu(frame, variable=self.type_var, values=["Pads", "Knobs", "Faders", "Switches"], command=self.update_bank_options)
        self.type_menu.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(frame, text="Source Bank:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.source_bank_var = ctk.StringVar()
        self.source_bank_menu = ctk.CTkOptionMenu(frame, variable=self.source_bank_var, command=self.update_dest_options)
        self.source_bank_menu.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(frame, text="Destination Bank:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.dest_bank_var = ctk.StringVar()
        self.dest_bank_menu = ctk.CTkOptionMenu(frame, variable=self.dest_bank_var)
        self.dest_bank_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=(0, 20), fill="x")
        ctk.CTkButton(button_frame, text="Apply Clone", command=self.apply_clone).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="right", expand=True, padx=5)
        
        self.update_bank_options("Pads")

    def update_bank_options(self, control_type):
        if control_type == "Pads":
            self.banks = ["A", "B", "C", "D"]
        else:
            self.banks = ["A", "B", "C"]
        
        self.source_bank_menu.configure(values=self.banks)
        self.source_bank_var.set(self.banks[0])
        self.update_dest_options(self.banks[0])

    def update_dest_options(self, selected_source):
        dest_options = [b for b in self.banks if b != selected_source]
        self.dest_bank_menu.configure(values=dest_options)
        if dest_options:
            self.dest_bank_var.set(dest_options[0])
        else:
            self.dest_bank_var.set("")

    def apply_clone(self):
        c_type = self.type_var.get()
        source_bank = self.source_bank_var.get()
        dest_bank = self.dest_bank_var.get()
        if not source_bank or not dest_bank:
            messagebox.showwarning("Warning", "Source and Destination banks must be selected.")
            return
        self.parent.apply_bank_clone(c_type, source_bank, dest_bank)
        self.destroy()

# --- Channel Mapper Window ---
class ChannelMapperWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.parent = parent
        self.title("Bulk MIDI Channel Mapper")
        self.geometry("350x250")

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Control Type Selection
        ctk.CTkLabel(frame, text="Control Type:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Pads")
        self.type_menu = ctk.CTkOptionMenu(frame, variable=self.type_var, values=["Pads", "Knobs", "Faders", "Switches"], command=self.update_bank_options)
        self.type_menu.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Bank Selection
        ctk.CTkLabel(frame, text="Target Bank:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.bank_var = ctk.StringVar(value="All")
        self.bank_menu = ctk.CTkOptionMenu(frame, variable=self.bank_var, values=["All", "A", "B", "C", "D"])
        self.bank_menu.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Channel Selection
        ctk.CTkLabel(frame, text="New Channel:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.channel_var = ctk.StringVar(value="Common")
        # Get channel names from the preset map
        channel_names = list(channel_map.keys())
        self.channel_menu = ctk.CTkOptionMenu(frame, variable=self.channel_var, values=channel_names)
        self.channel_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=(0, 20), fill="x")
        ctk.CTkButton(button_frame, text="Apply", command=self.apply_change).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="right", expand=True, padx=5)
        
        # Initialize bank options based on default type
        self.update_bank_options("Pads")

    def update_bank_options(self, control_type):
        # Pads have banks A-D, others have A-C
        if control_type == "Pads":
            banks = ["All", "A", "B", "C", "D"]
        else:
            banks = ["All", "A", "B", "C"]
        
        self.bank_menu.configure(values=banks)
        # Reset selection to "All" to avoid invalid states
        self.bank_var.set("All")

    def apply_change(self):
        c_type = self.type_var.get()
        bank = self.bank_var.get()
        channel = self.channel_var.get()
        self.parent.apply_bulk_channel(c_type, bank, channel)
        self.destroy()

# --- Pad Mapper Window ---
class PadMapperWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.parent = parent
        self.title("Set Pad Notes in Bulk")

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Target Pad Bank:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bank_var = ctk.StringVar(value="A")
        ctk.CTkOptionMenu(frame, variable=self.bank_var, values=["A", "B", "C", "D"]).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Starting Note:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        note_frame = ctk.CTkFrame(frame, fg_color="transparent")
        note_frame.grid(row=1, column=1, padx=0, pady=5, sticky="ew")
        self.note_names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        self.octaves = [str(i) for i in range(-1, 10)]
        self.start_note_name = ctk.StringVar(value="C")
        self.start_note_octave = ctk.StringVar(value="3")
        ctk.CTkOptionMenu(note_frame, variable=self.start_note_name, values=self.note_names).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkOptionMenu(note_frame, variable=self.start_note_octave, values=self.octaves).pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(frame, text="Mapping Type:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.map_type_var = ctk.StringVar(value="Chromatic (All Notes)")
        ctk.CTkOptionMenu(frame, variable=self.map_type_var, values=["Chromatic (All Notes)", "Diatonic (White Notes Only)"]).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=(0, 20), fill="x")
        ctk.CTkButton(button_frame, text="Apply", command=self.apply_mapping).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="right", expand=True, padx=5)

    def apply_mapping(self):
        bank = self.bank_var.get()
        start_note = self.start_note_name.get() + self.start_note_octave.get()
        map_type = "Diatonic" if "Diatonic" in self.map_type_var.get() else "Chromatic"
        self.parent.apply_pad_mapping(bank, start_note, map_type)
        self.destroy()

class ControlEditor(ctk.CTkToplevel):
    def __init__(self, parent, control_type, absolute_index, name=""):
        super().__init__(parent); self.transient(parent); self.grab_set(); self.parent = parent
        self.control_type = control_type; self.absolute_index = absolute_index; self.name = name
        self.title(f"Edit {control_type.capitalize()} {name or absolute_index}"); self.widgets = {}
        self.note_names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        self.octaves = [str(i) for i in range(-1, 10)]
        self.create_widgets(); self.populate_data(); self.protocol("WM_DELETE_WINDOW", self.cancel)

    def create_widgets(self):
        frame = ctk.CTkFrame(self); frame.pack(padx=10, pady=10, fill="both", expand=True)
        if self.control_type == "knob": fields = ["type", "channel", "cc", "min", "max", "midi_to_din", "msb", "lsb", "value"]
        elif self.control_type == "fader": fields = ["type", "channel", "cc", "min", "max", "midi_to_din"]
        elif self.control_type == "pad": fields = ["type", "channel", "mode", "aftertouch", "note", "program", "msb", "lsb", "off_color", "on_color", "midi_to_din"]
        else: fields = ["type", "channel", "mode", "midi_to_din", "cc", "invert", "note", "velocity", "program", "msb", "lsb", "key1", "key2"]
        self.build_fields(frame, fields); button_frame = ctk.CTkFrame(self); button_frame.pack(padx=10, pady=(0, 10), fill="x")
        ctk.CTkButton(button_frame, text="Save", command=self.save_changes).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, fg_color="gray").pack(side="right", expand=True, padx=5)

    def build_fields(self, parent, field_names):
        for i, field in enumerate(field_names):
            label = ctk.CTkLabel(parent, text=f"{field.replace('_', ' ').capitalize()}:"); label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            if field == "note":
                note_frame = ctk.CTkFrame(parent, fg_color="transparent")
                note_frame.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                name_widget = ctk.CTkOptionMenu(note_frame, values=self.note_names)
                name_widget.pack(side="left", expand=True, fill="x", padx=(0, 5))
                octave_widget = ctk.CTkOptionMenu(note_frame, values=self.octaves)
                octave_widget.pack(side="left", expand=True, fill="x")
                self.widgets['note_name'] = name_widget
                self.widgets['note_octave'] = octave_widget
                continue
            if field == "type":
                if self.control_type == "knob": choices = ["MIDI_CC", "AFTERTOUCH", "INC_DEC1", "INC_DEC2"]
                elif self.control_type == "fader": choices = ["MIDI_CC", "AFTERTOUCH"]
                elif self.control_type == "pad": choices = ["Note", "ProgramChange", "ProgramBank"]
                else: choices = ["CC", "Note", "ProgChange", "ProgBank", "Keystroke"]
                widget = ctk.CTkOptionMenu(parent, values=choices)
            elif field == "channel": widget = ctk.CTkOptionMenu(parent, values=list(channel_map.keys()))
            elif field in ["mode", "midi_to_din", "invert"]: widget = ctk.CTkOptionMenu(parent, values=["Toggle", "Momentary"] if field == "mode" else ["On", "Off"])
            elif field == "aftertouch": widget = ctk.CTkOptionMenu(parent, values=["Off", "Channel", "Poly"])
            elif field in ["off_color", "on_color"]: widget = ctk.CTkOptionMenu(parent, values=list(color_map.values()))
            elif field == "key1": widget = ctk.CTkOptionMenu(parent, values=list(key1_map_rev.keys()))
            elif field == "key2": widget = ctk.CTkOptionMenu(parent, values=list(key2_map_rev.keys()))
            else: widget = ctk.CTkEntry(parent)
            widget.grid(row=i, column=1, padx=5, pady=5, sticky="ew"); self.widgets[field] = widget
            
    def populate_data(self):
        data = self.parent.get_control_data(self.control_type, self.absolute_index, self.name)
        for field, widget in self.widgets.items():
            value = data.get(field)
            if field == 'note_name' and 'note' in data and data['note']:
                note_str = data['note']
                match = re.match(r'([A-G]#?)(-?\d+)$', note_str)
                if match:
                    self.widgets['note_name'].set(match.group(1))
                    self.widgets['note_octave'].set(match.group(2))
                continue
            if field == 'note_octave': continue
            
            if value is not None:
                if isinstance(widget, ctk.CTkOptionMenu): widget.set(str(value))
                else: widget.delete(0, 'end'); widget.insert(0, str(value))
                
    def save_changes(self):
        new_data = {};
        if 'note_name' in self.widgets and 'note_octave' in self.widgets:
            note_name = self.widgets['note_name'].get()
            note_octave = self.widgets['note_octave'].get()
            new_data['note'] = f"{note_name}{note_octave}"

        for field, widget in self.widgets.items():
            if field in ['note_name', 'note_octave']: continue
            value = widget.get()
            if isinstance(widget, ctk.CTkEntry) and value:
                try: new_data[field] = int(value)
                except ValueError: pass
            elif not isinstance(widget, ctk.CTkEntry): new_data[field] = value
            
        self.parent.set_control_data(self.control_type, self.absolute_index, new_data, self.name)
        self.parent.update_hotspot_labels()
        self.destroy()
        
    def cancel(self): self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AKAI MPK249 Visual Preset Editor")
        self.preset = MPK2Preset()
        self.current_control_bank = 0
        self.current_pad_bank = 0
        self.is_listening = False
        
        # --- WIDGET STORAGE ---
        self.knob_buttons = []
        self.fader_widgets = [] 
        self.switch_buttons = []
        self.pad_buttons = {} 
        self.daw_buttons = {} 
        
        # --- FIXED LAYOUT SETTINGS ---
        self.WINDOW_WIDTH = 1265; self.WINDOW_HEIGHT = 847
        self.IMAGE_WIDTH = 1058; self.IMAGE_HEIGHT = 847
        
        # --- BANK BUTTON SETTINGS ---
        self.control_bank_buttons = {}; self.pad_bank_buttons = {}
        self.ACTIVE_COLOR = "#337AB7"; self.INACTIVE_COLOR = "gray40"

        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}"); self.resizable(False, False)

        # Relative hotspot coordinates
        self.GROUP_COORDINATES = {
            'knobs': {'rx': 0.646800, 'ry': 0.277423}, 'faders': {'rx': 0.650800, 'ry': 0.332250},
            'switches': {'rx': 0.654800, 'ry': 0.447689}, 'daw': {'rx': 0.159940, 'ry': 0.313869},
            'pad_banks': {'rx': 0.238000, 'ry': 0.378613}, 'pads': {'rx': 0.2801000, 'ry': 0.282500},
            'control_bank': {'rx': 0.514000, 'ry': 0.450000},
        }

        # --- WINDOW LAYOUT ---
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)
        
        top_frame = ctk.CTkFrame(self, height=50); top_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        ctk.CTkButton(top_frame, text="Load from File...", command=self.load_preset_from_file).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(top_frame, text="Save to File...", command=self.save_preset_to_file).pack(side="left", padx=5, pady=5)
        self.preset_label = ctk.CTkLabel(top_frame, text="No Preset Loaded", font=("Arial", 16)); self.preset_label.pack(side="left", padx=20, pady=5)
        ctk.CTkButton(top_frame, text="Preset Info", command=self.edit_preset_info).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(top_frame, text="Set Pads", command=self.open_pad_mapper).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(top_frame, text="Set MIDI Chn", command=self.open_channel_mapper).pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(top_frame, text="Clone Bank", command=self.open_bank_cloner).pack(side="left", padx=5, pady=5)
        midi_frame = ctk.CTkFrame(self, height=50); midi_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        try:
            midi_out_temp = rtmidi.MidiOut(); midi_in_temp = rtmidi.MidiIn()
            self.out_ports = midi_out_temp.get_ports(); self.in_ports = midi_in_temp.get_ports()
            self.MIDI_IN_GET_NAME = "MIDIIN4 (MPK249)"; self.MIDI_OUT_GET_NAME = "" 
            self.MIDI_OUT_SEND_NAME = "MIDIOUT4 (MPK249)"; self.MIDI_IN_SEND_NAME = ""
            self.get_button = ctk.CTkButton(midi_frame, text="Get from Keyboard", command=self.get_preset_from_keyboard); self.get_button.pack(side="left", padx=5)
            self.send_button = ctk.CTkButton(midi_frame, text="Send to Keyboard", command=self.send_preset_to_keyboard); self.send_button.pack(side="left", padx=5)
            self.cancel_button = ctk.CTkButton(midi_frame, text="Cancel Listen", command=self.stop_midi_listener, fg_color="gray")
        except Exception as e:
            ctk.CTkLabel(midi_frame, text=f"Could not initialize MIDI: {e}", text_color="orange").pack(side="left", padx=5)
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent"); self.main_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        try:
            self.original_image = Image.open("keyboard.jpg")
            self.place_background_image(); self.place_static_hotspots()
        except FileNotFoundError:
            ctk.CTkLabel(self.main_frame, text="Error: keyboard.jpg not found.", font=("Arial", 20)).pack(fill="both", expand=True)
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def place_background_image(self):
        self.offset_x = (self.WINDOW_WIDTH - self.IMAGE_WIDTH) / 2
        self.offset_y = (self.WINDOW_HEIGHT - self.IMAGE_HEIGHT) / 2
        resized_image = self.original_image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        self.bg_image_ctk = ctk.CTkImage(light_image=resized_image, size=(self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        self.bg_label = ctk.CTkLabel(self.main_frame, text="", image=self.bg_image_ctk)
        self.bg_label.place(x=self.offset_x, y=self.offset_y)

    def place_static_hotspots(self):
        def create_hotspot(group_name, rel_x, rel_y, w, h, command):
            group_coords = self.GROUP_COORDINATES[group_name]
            base_x = group_coords['rx'] * self.IMAGE_WIDTH + self.offset_x
            base_y = group_coords['ry'] * self.IMAGE_HEIGHT + self.offset_y
            button = ctk.CTkButton(self.main_frame, text="", width=w, height=h, fg_color="gray30",
                                   hover_color="gray50", command=command, border_width=1, font=ctk.CTkFont(size=9))
            button.place(x=base_x + rel_x, y=base_y + rel_y); return button

        for i in range(8): self.knob_buttons.append(create_hotspot("knobs", i * 39, 0, 28, 28, lambda i=i: self.open_editor("knob", i)))
        for i in range(8): self.switch_buttons.append(create_hotspot("switches", i * 38.5, 0, 28, 18, lambda i=i: self.open_editor("switch", i)))
        
        for r in range(4):
            for c in range(4):
                p_index = (3 - r) * 4 + c
                self.pad_buttons[p_index] = create_hotspot("pads", c * 41, r * 41, 35, 35, lambda p=p_index: self.open_editor("pad", p))
        
        group_coords_faders = self.GROUP_COORDINATES['faders']
        base_x = group_coords_faders['rx'] * self.IMAGE_WIDTH + self.offset_x; base_y = group_coords_faders['ry'] * self.IMAGE_HEIGHT + self.offset_y
        for i in range(8):
            x_pos = base_x + i * 38.7
            btn = ctk.CTkButton(self.main_frame, text="", width=16, height=78, fg_color="gray30", hover_color="gray50", border_width=1, command=lambda i=i: self.open_editor("fader", i))
            btn.place(x=x_pos, y=base_y)
            top_label = ctk.CTkLabel(self.main_frame, text="", width=16, height=15, font=ctk.CTkFont(size=9), fg_color="transparent")
            top_label.place(x=x_pos, y=base_y + 2)
            bottom_label = ctk.CTkLabel(self.main_frame, text="", width=16, height=15, font=ctk.CTkFont(size=9), fg_color="transparent")
            bottom_label.place(x=x_pos, y=base_y + 78 - 15 - 2)
            self.fader_widgets.append({'button': btn, 'top_label': top_label, 'bottom_label': bottom_label})

        group_coords_pad = self.GROUP_COORDINATES['pad_banks']
        for i, label in enumerate(["A", "B", "C", "D"]):
            btn = ctk.CTkButton(self.main_frame, text=label, width=25, height=20, fg_color=self.INACTIVE_COLOR, command=lambda v=label: self.set_pad_bank(v))
            btn.place(x=group_coords_pad['rx'] * self.IMAGE_WIDTH + self.offset_x, y=group_coords_pad['ry'] * self.IMAGE_HEIGHT + self.offset_y + i * 23)
            self.pad_bank_buttons[label] = btn

        group_coords_ctrl = self.GROUP_COORDINATES['control_bank']
        base_x_ctrl = group_coords_ctrl['rx'] * self.IMAGE_WIDTH + self.offset_x; base_y_ctrl = group_coords_ctrl['ry'] * self.IMAGE_HEIGHT + self.offset_y
        for i, label in enumerate(["A", "B", "C"]):
            btn = ctk.CTkButton(self.main_frame, text=label, width=25, height=18, fg_color=self.INACTIVE_COLOR, command=lambda v=label: self.set_control_bank(v))
            btn.place(x=base_x_ctrl + (i * 28), y=base_y_ctrl); self.control_bank_buttons[label] = btn
        
        daw_controls = [{'name': 'Up', 'rel_x': 25, 'rel_y': 0}, {'name': 'Left', 'rel_x': 0, 'rel_y': 22}, {'name': 'Enter', 'rel_x': 25, 'rel_y': 22}, {'name': 'Right', 'rel_x': 50, 'rel_y': 22}, {'name': 'Down', 'rel_x': 25, 'rel_y': 44}]
        for ctrl in daw_controls: self.daw_buttons[ctrl['name']] = create_hotspot("daw", ctrl['rel_x'], ctrl['rel_y'], 22, 18, lambda name=ctrl['name']: self.open_editor("daw", name=name))
        
        self.set_control_bank("A"); self.set_pad_bank("A"); self.update_hotspot_labels()

    def update_hotspot_labels(self):
        if not self.preset or not self.preset.sysex_data: return
        LEGEND = {"ProgramBank": "PGB", "AFTERTOUCH": "AFT", "INC_DEC1": "ID1", "Keystroke": "KEY"}
        try:
            control_offset = self.current_control_bank * 8
            for i in range(8):
                abs_idx = control_offset + i + 1
                knob_data = self.preset.get_knob(abs_idx); k_type = knob_data.get("type", "")
                self.knob_buttons[i].configure(text=str(knob_data.get("cc", "")) if k_type in ["MIDI_CC", "INC_DEC2"] else LEGEND.get(k_type, ""))
                fader_data = self.preset.get_fader(abs_idx); f_type = fader_data.get("type")
                self.fader_widgets[i]['button'].configure(text="")
                self.fader_widgets[i]['top_label'].configure(text=str(fader_data.get("cc", "")) if f_type == "MIDI_CC" else str(fader_data.get("max", "")))
                self.fader_widgets[i]['bottom_label'].configure(text="" if f_type == "MIDI_CC" else str(fader_data.get("min", "")))
                switch_data = self.preset.get_switch(abs_idx); s_type = switch_data.get("type", ""); text = ""
                if s_type == "CC": text = str(switch_data.get("cc", ""))
                elif s_type == "Note": text = str(switch_data.get("note", ""))
                elif s_type == "ProgChange": text = f"P{switch_data.get('program', '')}"
                else: text = LEGEND.get(s_type, s_type)
                self.switch_buttons[i].configure(text=text)

            pad_offset = self.current_pad_bank * 16
            for i in range(16):
                pad_data = self.preset.get_pad(pad_offset + i + 1); p_type = pad_data.get("type", ""); text = ""
                if p_type == "Note": text = str(pad_data.get("note", ""))
                elif p_type == "ProgramChange": text = f"P{pad_data.get('program', '')}"
                else: text = LEGEND.get(p_type, p_type)
                self.pad_buttons[i].configure(text=text)

            for name, button in self.daw_buttons.items():
                daw_data = self.preset.get_daw(name); d_type = daw_data.get("type", ""); text = ""
                if d_type == "CC": text = str(daw_data.get("cc", ""))
                elif d_type == "Note": text = str(daw_data.get("note", ""))
                elif d_type == "ProgChange": text = f"P{daw_data.get('program', '')}"
                else: text = LEGEND.get(d_type, d_type)
                button.configure(text=text)
        except Exception as e: print(f"Error updating labels: {e}")

    def set_control_bank(self, value):
        self.current_control_bank = ["A", "B", "C"].index(value)
        for label, button in self.control_bank_buttons.items():
            button.configure(fg_color=self.ACTIVE_COLOR if label == value else self.INACTIVE_COLOR)
        self.update_hotspot_labels()

    def set_pad_bank(self, value):
        self.current_pad_bank = ["A", "B", "C", "D"].index(value)
        for label, button in self.pad_bank_buttons.items():
            button.configure(fg_color=self.ACTIVE_COLOR if label == value else self.INACTIVE_COLOR)
        self.update_hotspot_labels()
            
    def open_editor(self, control_type, relative_index=0, name=""):
        if not self.preset.sysex_data: messagebox.showerror("Error", "Please load a preset file first."); return
        if control_type in ["knob", "fader", "switch"]: absolute_index = self.current_control_bank * 8 + relative_index + 1; name = f"{['A','B','C'][self.current_control_bank]}{relative_index + 1}"
        elif control_type == "pad": absolute_index = self.current_pad_bank * 16 + relative_index + 1; name = f"{['A','B','C','D'][self.current_pad_bank]}{relative_index + 1}"
        elif control_type == "daw": absolute_index = daw_names.index(name) + 1
        ControlEditor(self, control_type, absolute_index, name)

    def open_pad_mapper(self):
        if not self.preset.sysex_data: messagebox.showerror("Error", "Please load a preset file first."); return
        PadMapperWindow(self)

    def apply_pad_mapping(self, bank, start_note, map_type):
        try:
            start_midi_note = note_map.get(start_note)
            if start_midi_note is None: messagebox.showerror("Error", f"Invalid starting note: {start_note}"); return

            bank_index = ["A", "B", "C", "D"].index(bank)
            start_pad_index = bank_index * 16 + 1
            current_midi_note = start_midi_note

            if map_type == "Chromatic":
                for i in range(16):
                    target_midi_note = current_midi_note + i
                    if 0 <= target_midi_note <= 127:
                        note_name = note_map_rev.get(target_midi_note)
                        self.preset.set_pad(start_pad_index + i, type="Note", note=note_name)
            elif map_type == "Diatonic":
                white_key_remainders = {0, 2, 4, 5, 7, 9, 11}
                for i in range(16):
                    if i == 0:
                        while (current_midi_note % 12) not in white_key_remainders: current_midi_note += 1
                    else:
                        current_midi_note += 1
                        while (current_midi_note % 12) not in white_key_remainders: current_midi_note += 1
                    if 0 <= current_midi_note <= 127:
                        note_name = note_map_rev.get(current_midi_note)
                        self.preset.set_pad(start_pad_index + i, type="Note", note=note_name)

            self.update_hotspot_labels()
            messagebox.showinfo("Success", f"Pad Bank {bank} has been mapped.")
        except Exception as e: messagebox.showerror("Error", f"An error occurred during mapping: {e}")

    def open_channel_mapper(self):
        if not self.preset.sysex_data: messagebox.showerror("Error", "Please load a preset file first."); return
        ChannelMapperWindow(self)

    def apply_bulk_channel(self, c_type, bank, new_channel):
        try:
            # Determine parameters based on control type
            if c_type == "Pads":
                items_per_bank = 16
                banks = ["A", "B", "C", "D"]
                set_func = self.preset.set_pad
                total_items = 64
            else: # Knobs, Faders, Switches
                items_per_bank = 8
                banks = ["A", "B", "C"]
                total_items = 24
                if c_type == "Knobs": set_func = self.preset.set_knob
                elif c_type == "Faders": set_func = self.preset.set_fader
                elif c_type == "Switches": set_func = self.preset.set_switch

            # Calculate range of indices
            if bank == "All":
                start_idx = 1
                end_idx = total_items + 1
            else:
                bank_idx = banks.index(bank)
                start_idx = (bank_idx * items_per_bank) + 1
                end_idx = start_idx + items_per_bank

            # Apply changes
            for i in range(start_idx, end_idx):
                set_func(i, channel=new_channel)

            # Update GUI and notify
            self.update_hotspot_labels() # In case channel affects display
            target_str = f"All {c_type}" if bank == "All" else f"{c_type} Bank {bank}"
            messagebox.showinfo("Success", f"Channel for {target_str} set to {new_channel}.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during bulk update: {e}")
    def open_bank_cloner(self):
        if not self.preset.sysex_data:
            messagebox.showerror("Error", "Please load a preset file first.")
            return
        BankClonerWindow(self)

    def apply_bank_clone(self, control_type, source_bank, dest_bank):
        try:
            # Determine parameters based on control type
            if control_type == "Pads":
                items_per_bank = 16
                banks = ["A", "B", "C", "D"]
                get_func = self.preset.get_pad
                set_func = self.preset.set_pad
            else: # Knobs, Faders, Switches
                items_per_bank = 8
                banks = ["A", "B", "C"]
                if control_type == "Knobs":
                    get_func = self.preset.get_knob
                    set_func = self.preset.set_knob
                elif control_type == "Faders":
                    get_func = self.preset.get_fader
                    set_func = self.preset.set_fader
                elif control_type == "Switches":
                    get_func = self.preset.get_switch
                    set_func = self.preset.set_switch
            
            # Calculate start indices for source and destination banks
            source_bank_idx = banks.index(source_bank)
            dest_bank_idx = banks.index(dest_bank)
            
            source_start_idx = (source_bank_idx * items_per_bank) + 1
            dest_start_idx = (dest_bank_idx * items_per_bank) + 1

            # Perform the clone operation
            for i in range(items_per_bank):
                # Get all parameters from the source control
                source_data = get_func(source_start_idx + i)
                
                # Apply all those parameters to the destination control
                set_func(dest_start_idx + i, **source_data)
            
            # Update GUI and notify the user
            self.update_hotspot_labels()
            messagebox.showinfo("Success", f"{control_type} Bank {source_bank} has been cloned to Bank {dest_bank}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while cloning: {e}")       

    def get_control_data(self, control_type, index, name=""):
        if control_type == "knob": return self.preset.get_knob(index)
        if control_type == "fader": return self.preset.get_fader(index)
        if control_type == "pad": return self.preset.get_pad(index)
        if control_type == "switch": return self.preset.get_switch(index)
        if control_type == "daw": return self.preset.get_daw(name)
        
    def set_control_data(self, control_type, index, data, name=""):
        if control_type == "knob": self.preset.set_knob(index, **data)
        if control_type == "fader": self.preset.set_fader(index, **data)
        if control_type == "pad": self.preset.set_pad(index, **data)
        if control_type == "switch": self.preset.set_switch(index, **data)
        if control_type == "daw": self.preset.set_daw(name, **data)
        
    def load_preset_from_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("SysEx files", "*.syx")]);
        if filepath:
            self.preset.load_from_file(filepath)
            if self.preset.sysex_data: self.update_preset_label(); self.update_hotspot_labels(); messagebox.showinfo("Success", "Preset loaded.")
            
    def save_preset_to_file(self):
        if not self.preset or not self.preset.sysex_data: messagebox.showerror("Error", "No data to save."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".syx", filetypes=[("SysEx files", "*.syx")])
        if filepath: self.preset.save_to_file(filepath)
        
    def update_preset_label(self):
        name = self.preset.get_preset_name(); num = self.preset.get_preset_number(); model = self.preset.get_model()
        self.preset_label.configure(text=f"Loaded: '{name}' (#{num}) on {model}")
        
    def edit_preset_info(self):
        if not self.preset or not self.preset.sysex_data: messagebox.showerror("Error", "Load a preset first."); return
        new_name = ctk.CTkInputDialog(text="New name:", title="Edit Preset Name").get_input()
        if new_name is not None: self.preset.set_preset_name(new_name)
        new_num_str = ctk.CTkInputDialog(text="New number (1-30):", title="Edit Preset Number").get_input()
        try:
            if new_num_str:
                new_num = int(new_num_str)
                if 1 <= new_num <= 30: self.preset.set_preset_number(new_num - 1)
                else: messagebox.showerror("Error", "The number must be between 1 and 30.")
        except ValueError: pass
        self.update_preset_label()

    def midi_listener_thread(self, midi_in):
        sysex_buffer = bytearray(); is_assembling = False
        while self.is_listening:
            msg = midi_in.get_message()
            if msg:
                chunk, _ = msg
                if chunk and chunk[0] == 0xF0: sysex_buffer = bytearray(chunk); is_assembling = True
                elif is_assembling: sysex_buffer.extend(chunk)
                if is_assembling and sysex_buffer and sysex_buffer[-1] == 0xF7:
                    self.is_listening = False; self.after(0, self.load_preset_from_data, bytes(sysex_buffer))
            time.sleep(0.001)
        midi_in.close_port(); self.after(0, self.reset_get_button)

    def load_preset_from_data(self, sysex_bytes):
        self.preset = MPK2Preset(data=sysex_bytes)
        self.update_preset_label(); self.update_hotspot_labels(); messagebox.showinfo("Success", f"Preset received ({len(sysex_bytes)} bytes).")

    def get_preset_from_keyboard(self):
        if self.is_listening: return
        try:
            out_idx = next((i for i, p in enumerate(self.out_ports) if self.MIDI_OUT_GET_NAME in p), None)
            in_idx = next((i for i, p in enumerate(self.in_ports) if self.MIDI_IN_GET_NAME in p), None)
            if out_idx is None or in_idx is None: messagebox.showerror("MIDI Error", "'Get' ports not found."); return
            
            midi_in = rtmidi.MidiIn(); midi_in.open_port(in_idx); midi_in.ignore_types(sysex=False)
            self.is_listening = True
            threading.Thread(target=self.midi_listener_thread, args=(midi_in,), daemon=True).start()
            
            midi_out = rtmidi.MidiOut(); midi_out.open_port(out_idx)
            midi_out.send_message([0xF0, 0x47, 0x00, 0x24, 0x31, 0x00, 0x01, 0x00, 0xF7])
            midi_out.close_port(); del midi_out
            
            self.get_button.configure(state="disabled"); self.send_button.configure(state="disabled")
            self.cancel_button.pack(side="left", padx=5)
        except Exception as e:
            messagebox.showerror("MIDI Error", f"Error: {e}"); self.reset_get_button()

    def stop_midi_listener(self):
        if self.is_listening: self.is_listening = False

    def reset_get_button(self):
        self.get_button.configure(state="normal"); self.send_button.configure(state="normal")
        self.cancel_button.pack_forget()

    def send_preset_to_keyboard(self):
        if not self.preset or not self.preset.sysex_data: messagebox.showerror("Error", "No preset to send."); return
        try:
            out_idx = next((i for i, p in enumerate(self.out_ports) if self.MIDI_OUT_SEND_NAME in p), None)
            if out_idx is None: messagebox.showerror("MIDI Error", f"Port '{self.MIDI_OUT_SEND_NAME}' not found."); return
            midi_out = rtmidi.MidiOut(); midi_out.open_port(out_idx)
            midi_out.send_message(list(self.preset.sysex_data))
            midi_out.close_port(); del midi_out
            messagebox.showinfo("Success", f"Preset sent to {self.out_ports[out_idx]}")
        except Exception as e: messagebox.showerror("MIDI Error", f"Send error: {e}")

    def on_closing(self):
        self.is_listening = False; time.sleep(0.05); self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
