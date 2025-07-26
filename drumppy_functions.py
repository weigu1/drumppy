"""  drumppy functions """

from email.mime import message
import os
import time
from time import sleep
from datetime import datetime
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage, tempo2bpm, get_output_names, open_output, open_input
from drumppy_instruments import instruments
from drumppy_music_genres import music_genres
from drumppy_patterns.drumppy_patterns_template import text as template
import json
from importlib import import_module # stl dynamically import module (name known during runtime)

class DrumppyFunctions:
    def __init__(self, flags_2_main, queue_2_main, queue_2_gui):
        """ Initialize the DP100Functions class with queues for communication. """
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
        self.flags_2_main = flags_2_main
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir)  # Set working directory to script's directory
        self.midi_ports = self.get_midi_ports()
        self.instruments = instruments
        self.instruments_names = ""
        self.drum_patterns_module_name = ""
        self.drum_patterns_names = ""
        self.chosen_midi_port = ""
        self.chosen_instrument = ""
        self.chosen_genre = ""
        self.chosen_pattern = ""
        self.chosen_channel = 9
        self.chosen_bpm = 120
        self.chosen_song = []
        self.steps_2_play = 16
        self.flag_play = True
        self.roll_seq = [1,9],[1,6,11],[1,5,9,13],[1,4,7,10,13],[1,4,7,10,13,16],[1,3,6,8,11,13,16],[1,3,5,7,9,11,13,15]

    def create_music_genres_files(self):
        """Create a pattern file for music genre if not existent."""
        try:
            for genre in music_genres:
                filename = f"drumppy_patterns/drumppy_patterns_{genre}.py"
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        f.write(f"# Drum patterns for {genre}\n")
                        f.write('drum_patterns = [[{"pattern_name":"' + genre + '_beat_1",')
                        f.write(template)
            os.chdir(self.script_dir)
            text = "Music genres files created successfully."
            print(text)
            self.queue_2_gui.put(text)
        except Exception as e:
            text = f"Error creating music genres files: {e}!"
            print(text)
            self.queue_2_gui.put(text)

    def get_midi_ports(self):
        """Function to retrieve available MIDI output ports."""
        midi_ports = []
        try:
            for port in get_output_names():
                midi_ports.append(port)
            text = "Midi_ports:\n" + '\n'.join(midi_ports)
            self.queue_2_gui.put(text)
            return midi_ports
        except Exception as e:
            text = f"Error retrieving MIDI output ports: {e}!"
            print(text)
            self.queue_2_gui.put(text)
            return []

    def load_drum_patterns(self):
        """ Load drum_patterns and their names """
        try:
            #print(self.drum_patterns_module_name)
            drum_patterns_module = import_module(self.drum_patterns_module_name)
            self.drum_patterns = drum_patterns_module.drum_patterns
            self.chosen_pattern = self.drum_patterns_names[0]
        except Exception as e:
            text = f"Error retrieving drum patterns: {e}!"
            print(text)
            self.queue_2_gui.put(text)

    def check_port(self, midi_port = "CH345:CH345 MIDI 1"):  # "USB MIDI 2x2:USB MIDI 2x2 MIDI 1"
        """Function to check if a specific MIDI port is available."""
        try:
            for port in get_output_names():
                if midi_port in port:
                    return port
            return "None"
        except Exception as e:
            text = f"Error retrieving MIDI output port: {e}"
            print(text)
            self.queue_2_gui.put(text)

    def play_drum_pattern(self):
        """Function to send drum pattern to the MIDI output port."""
        if self.chosen_midi_port == "":
            text = ("No valid midi port! Connect first!")
            print(text)
            self.queue_2_gui.put(text)
            self.flags_2_main["flag_stop_play_patt"].set()
            return
        try:
            p_index = self.drum_patterns_names.index(self.chosen_pattern)
            i_index = self.instruments_names.index(self.chosen_instrument)
            drum_pattern = self.drum_patterns[int(p_index)]
            instrument = self.instruments[int(i_index)]
            #ch = instrument["midi_channel"]
            ch = int(self.chosen_channel)-1 # mido starts with 0
            nr_dr = drum_pattern[0]["nr_of_drums"]
            #sixteenth_time = 60 / int(self.chosen_bpm) / 4 # 16th per quarter
            time_1_256 = 60 / int(self.chosen_bpm) / 64    # 64 256th per quarter
            # get roll and delay of pattern in an array

            roll = [[0]*16 for _ in range(8)]
            delay = [[0]*16 for _ in range(8)]
            #stretch = [[0]*16 for _ in range(8)]
            for j in range(1, int(self.steps_2_play) + 1): # steps to play
                for i in range(1,nr_dr + 1):
                    if drum_pattern[i][j][0] & 0b0000_1110 != 0:
                        roll[i-1][j-1] = (drum_pattern[i][j][0] & 0b0001_1110) >> 1
                    if len(drum_pattern[i][j]) > 2: # we get different stretch and/or a delay
                        delay[i-1][j-1] = drum_pattern[i][j][2]
                    #if len(drum_pattern[i][j]) > 3:
                    #    stretch[i-1][j-1] = drum_pattern[i][j][3]
            #print("stretch: ", stretch)
            #print("roll: ", roll)
            #print("delay ", delay)
            # play loop
            with open_output(self.chosen_midi_port) as outport:
                for j in range(1, int(self.steps_2_play) + 1): # steps to play
                    #text = f"Tick:\n{j}"  # sorry queue is too slow
                    #self.queue_2_gui.put(text)
                    for k in range(1,17):
                        for i in range(1,nr_dr + 1):
                            if drum_pattern[i]["drum_name"] == "":
                                break
                            if drum_pattern[i]["muted"] == "n":
                                if roll[i-1][j-1] == 0  and k == (1 + delay[i-1][j-1]):
                                    if drum_pattern[i][j][0]:
                                        msg = Message('note_on', note=instrument[drum_pattern[i]["drum_name"]], velocity=drum_pattern[i][j][1], channel=ch)
                                        outport.send(msg)
                                    else:
                                        msg = Message('note_off', note=instrument[drum_pattern[i]["drum_name"]],
                                        velocity=0, channel=ch)
                                        outport.send(msg)
                                if roll[i-1][j-1] > 1:
                                    rk = self.roll_seq[roll[i-1][j-1]-2]
                                    for l in range(0,len(rk)):
                                        rk[l] = rk[l] + delay[i-1][j-1]
                                        if rk[l] > 16:
                                            rk[l] = 0
                                    for item in rk:
                                        if k == item:
                                            msg = Message('note_on', note=instrument[drum_pattern[i]["drum_name"]], velocity=drum_pattern[i][j][1], channel=ch)
                                            outport.send(msg)
                        sleep(time_1_256)
            text = f"Pattern_end\n"
            self.queue_2_gui.put(text)


        except Exception as e:
            text = f"Error playing drum pattern: {e}"
            print(text)
            self.queue_2_gui.put(text)


    def create_and_save_midi_file(self):
        pass







    def play_song(self):
        """Function to play a song of patterns."""
        if self.chosen_song == []:
            text = ("No valid song! Choose song first!")
            print(text)
            self.queue_2_gui.put(text)
            self.flags_2_main["flag_stop_play_song"].set()
            return
        print(self.chosen_song)
        text = f"Playing song: {self.chosen_song[0]['song_name']}"
        nr_of_segments = len(self.chosen_song)
        print(nr_of_segments)
        if nr_of_segments < 2:
            text = "No patterns in song!"
            print(text)
            self.queue_2_gui.put(text)
            return
        for i in range(1, nr_of_segments):
            patt_cnt = 0
            for pattern in self.chosen_song[i]:
                patt_cnt = patt_cnt + 1
                self.chosen_pattern = pattern[0]
                text = f"Next_pattern:\n{i}\n{patt_cnt}\n{self.chosen_pattern}"
                self.queue_2_gui.put(text)
                repeat = pattern[1]
                while(repeat):
                    if self.flags_2_main["flag_stop_play_song"].is_set():
                        self.flags_2_main["flag_stop_play_patt"].clear()
                        return
                    text = f"Playing pattern: {pattern[0]}"
                    print(text)
                    self.queue_2_gui.put(text)
                    self.play_drum_pattern()
                    repeat = repeat-1
        text = f"Song_end"
        self.queue_2_gui.put(text)





    def send_identity_request(self, chosen_midi_port, timeout=2):
        """
        Sends a MIDI Identity Request SysEx message and analyzes the reply.
        Returns a dictionary with parsed identity information or None if no reply is received.
        """
        identity_request = [0x7E, 0x7F, 0x06, 0x01]
        msg = Message('sysex', data=identity_request, time=0)  # mido excludes F0/F7
        try:
            with open_output(chosen_midi_port) as outport, open_input(chosen_midi_port) as inport:
                print(msg.hex())
                outport.send(msg)
                text = f"Sent Identity Request to {chosen_midi_port}, waiting for reply..."
                self.queue_2_gui.put(text)
                for reply in inport.iter_pending():
                    pass  # Clear any old messages
                start_time = time.time()
                while time.time() - start_time < timeout:
                    for msg in inport.iter_pending():
                        print(f"Received SysEx message: {msg.hex()}") # Debugging line
                        print(msg.type)
                        if msg.type == 'sysex':
                            data = list(msg.data)
                            print(f"Received SysEx message data: {data}")
                            if len(data) >= 7 and data[1] == 0x7E and data[3] == 0x06 and data[4] == 0x02:
                                manufacturer_id = data[5:8]
                                family_code = data[8:10]
                                model_number = data[10:12]
                                version = data[12:16]
                                identity = {"manufacturer_id": manufacturer_id,
                                            "family_code": family_code,
                                            "model_number": model_number,
                                            "version": version
                                          }
                                text = f"Received identity reply: {identity}"
                                print(text)
                                self.queue_2_gui.put(text)
                                return identity
                    time.sleep(0.01)  # Sleep briefly to avoid busy-waiting
                text = "Time out: No identity reply received."
                print(text)
                self.queue_2_gui.put(text)
                return None
        except Exception as e:
            text = f"Error opening port while sending identity request: {e}"
            print(text)
            self.queue_2_gui.put(text)
            return None

    def play_some_notes(self, chosen_midi_port):
        """Function to play some notes on the MIDI output port."""
        text = "Playing some notes on all channels"
        print(text)
        self.queue_2_gui.put(text)
        try:
            with open_output(chosen_midi_port) as outport:
                for i in range(40, 60):
                    for ch in range(16):
                        msg = Message('note_on', note=i, velocity=64, channel=ch)
                        outport.send(msg)
                sleep(1)
                for i in range(38, 80):
                    for ch in range(16):
                        msg = Message('note_off', note=i, velocity=64, channel=ch)
                        outport.send(msg)
            text = "Done playing notes."
            print(text)
            self.queue_2_gui.put(text)
        except Exception as e:
            text = f"Error playing notes: {e}"
            print(text)
            self.queue_2_gui.put(text)

if __name__ == "__main__":

    # Change this to your MIDI port name (omit the number with the colon)
    MIDI_PORT = "CH345:CH345 MIDI 1"

    dp = DrumppyFunctions(queue_2_main=None, queue_2_gui=None, queue_2_png=None)

    instrument = instruments[1]["cyclone_tt_78"]
    print("List of ports found: ", dp.get_midi_ports())
    port_name = dp.check_port(MIDI_PORT)
    if port_name != "None":
        print(f"Using port: {port_name}")
        with open_output(port_name) as outport:
            for i in range(3):
                dp.play_song()
            print("Finished playing song.")
    else:
        print("No MIDI output port found. Please check your MIDI device connection.")













    def get_instruments_names_old(self, instruments):
        """Function to get the names of instruments."""
        instr_dir = {}
        try:
            for i in instruments:
                instr_dir[i] = {
                    "instrument_name": instruments[i]["instrument_name"],
                    "instrument_port": instruments[i]["midi_port"],
                    "instrument_channel": instruments[i]["midi_channel"]
                }
            # Convert dicts to strings for display
            text = "Instruments:\n" + json.dumps(instr_dir)
            self.queue_2_gui.put(text)
            return instr_dir
        except Exception as e:
            text = f"Error retrieving instrument names: {e}!"
            print(text)
            self.queue_2_gui.put(text)
            return []

    def get_patterns_names(self, drum_patterns):
        """Function to get the names of drum patterns."""
        dp_list = []
        try:
            for pattern in drum_patterns:
                dp_list.append(drum_patterns[pattern][0]["pattern_name"])
            text = "Drum_patterns:\n" + '\n'.join(dp_list)
            self.queue_2_gui.put(text)
            return dp_list
        except Exception as e:
            text = f"Error retrieving drum pattern names: {e}!"
            print(text)
            self.queue_2_gui.put(text)
            return []
