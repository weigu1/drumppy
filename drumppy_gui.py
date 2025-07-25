import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.font as tkFont
from time import strftime, localtime, sleep
import queue
from functools import partial # to pass argument from profile buttons
import json
from drumppy_instruments import instruments
from drumppy_music_genres import music_genres
from importlib import import_module # stl dynamically import module (name known during runtime)
import copy

class GUI:
    def __init__(self, flags_2_main, queue_2_main, queue_2_gui):
        self.music_genres = music_genres
        self.standard_font = ["Helvetica", 12, "bold"]
        self.standard_font_big = ["Helvetica", 20, "bold"]
        self.standard_font_small = ["Helvetica", 8, "bold"]
        self.textbox_font = ["Courier", 12, "bold"]
        self.welcome_txt = "Hello to DRUMPPY V0.3 alpha (2025)"
        self.active_profile = 0
        self.state = 0
        self.flags_2_main = flags_2_main
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
        self.midi_port_names = [""]
        self.instruments = instruments
        self.instruments_names = []
        self.instruments_channels = []
        self.instruments_ports = []
        #self.channels_nrs = [str(i) for i in range(1, 17)]  # MIDI channels 1-16
        #self.song_patt_repeats = [str(i) for i in range(1, 9)]
        #self.play_nr_of_steps = [str(i) for i in range(1, 17)]
        self.drum_patterns = []
        self.current_drum_pattern = []
        self.drum_patterns_names = []
        self.drum_patterns_module_filename = ""
        self.chosen_instrument_drum_names = []
        self.chosen_midi_port = ""
        self.chosen_instrument_name = ""
        self.chosen_channel = 1
        self.chosen_pattern_name = ""
        self.chosen_pattern_index = 0
        self.lock = ""
        self.velocity_1 = 64
        self.velocity_2 = 100
        self.velocity_3 = 120
        self.bpm = [60, 80, 100, 120, 150, 180]
        self.song = []
        self.song_name = ""
        #self.flag_play_patt_finished = False
        self.seg_now = 0
        self.seg_prev = 0
        self.patt_in_seg_now = 0
        self.patt_in_seg_prev = 0
         # Dictionary for widget texts (inside:message)
        self.widget_texts_dict = {"Title" : self.welcome_txt,
                                  "Midi_ports" : "MIDI ports",
                                  "Connect" : "Connect",
                                  "Connected" : "Connected",
                                  "Rescan" : "Rescan MIDI ports",
                                  "Chosen_port" : "Chosen MIDI port:",
                                  "Instruments" : "Instrument",
                                  "Choose_instrument" : "Choose instrument",
                                  "Rescan_instruments" : "Rescan instruments",
                                  "Channels" : "Channel",
                                  "Patterns" : "Pattern",
                                  "Genre" : "Music genre",
                                  "Save_pattern" : "SAVE pattern",
                                  "Save_new_pattern" : "SAVE new pattern",
                                  "Open_song_editor" : "Open song Editor",
                                  "Close_song_editor" : "Close song Editor",
                                  "save_patt_2_midi" : "SAVE pattern 2 midi",
                                  "Open_song" : "OPEN song file",
                                  "New_pattern" : "New pattern name",
                                  "Pattern_editor": "Pattern editor",
                                  "Velocity" : "MIDI velocity: ",
                                  "Roll" : "Roll",
                                  "Stretch" : "Stretch (steps)",
                                  "Delay" : "Delay (1/256)",

                                  "Tick_nr" : "Steps_2_play",
                                  "Free" : "Free",
                                  "Locked" : "Lock",

                                  "Song_editor" : "Song editor",
                                  "Song_expl" : "1 Segment contains\n4 pattern + repeat",
                                  "Play_pattern_once" : "PLAY pattern 1x",
                                  "Play_pattern" : "PLAY pattern",
                                  "Stop_playing_pattern" : "STOP pattern",
                                  "Play_song" : "PLAY song",
                                  "Stop_playing_song" : "STOP song",

                                  "Save_midifile": "Save song as midifile",
                                  "Clear Textwindow" : "Clear Textwindow",
                                  "Quit" : "Quit"
                                 }
        self.widget_texts_list = list(self.widget_texts_dict.keys())
        self.padx = 5
        self.pady = 5
        self.ipady = 6
        self.song_grid_visible = False
        self.button_width_big = 38
        self.button_width = 20
        self.button_width_small = 16
        self.butt_pad_width = 5
        self.butt_mute_width = 6
        self.butt_seg_width = 6
        self.combo_repeat_width = 3
        self.combo_width = 25
        self.combo_drum_width = 20
        self.check_mute_width = 2
        self.VI_label_width = 10
        self.text_win_width = 106
        self.text_win_height = 6
        self.end = END

    def set_flag(self, flag, message):
        flag.set()
        if message != "":
            self.txt_win.insert(self.end, f"{message}\n")

    def check_queue_from_main(self):
        try:
            message = self.queue_2_gui.get_nowait()
            self.textwindow_insert(f"{message}\n")
            message = message.split('\n')
            if message[0] == "Error:":
                self.textwindow_insert(f"{message}\n")
            elif message[0] == "Midi_ports:":
                self.midi_port_names = message[1:]
                print(self.midi_port_names)
                try:
                    self.combo_midi_port['values'] = self.midi_port_names
                    self.combo_midi_port.current(1)
                except:
                    pass
            elif message[0] == "Next_pattern:":
                self.seg_now = int(message[1])-1
                self.seg_prev = self.seg_now-1
                if self.seg_prev == -1:
                    self.seg_prev = 15
                self.patt_in_seg_now  = int(message[2])-1
                if self.patt_in_seg_now == 0:
                    self.combo_song_patt[3].configure(style = "default.TCombobox")
                    self.combo_song_patt_repeat[3].configure(style = "default.TCombobox")
                else:
                    patt_in_seg_prev = self.patt_in_seg_now-1
                    self.combo_song_patt[patt_in_seg_prev].configure(style = "default.TCombobox")
                    self.combo_song_patt_repeat[patt_in_seg_prev].configure(style = "default.TCombobox")
                self.butt_seg[self.seg_now].configure(style="pressed.TButton")
                self.butt_seg[self.seg_prev].configure(style="default.TButton")
                self.combo_song_patt[self.patt_in_seg_now].configure(style = "highligted.TCombobox")
                self.combo_song_patt_repeat[self.patt_in_seg_now].configure(style = "highligted.TCombobox")
                self.load_drum_pattern(message[3])

            elif message[0] == "Song_end":
                self.butt_seg[self.seg_now].configure(style="default.TButton")
                self.combo_song_patt[self.patt_in_seg_now].configure(style = "default.TCombobox")
                self.combo_song_patt_repeat[self.patt_in_seg_now].configure(style = "default.TCombobox")

            elif message[0] == "Pattern_end":
                self.butt_play_patt_once.configure(style="important.TButton")

            elif message[0] == "No valid midi port! Connect first!":
                self.butt_play_patt_once.configure(style="important.TButton")
                self.butt_play_patt.configure(style="important.TButton")
                self.butt_stop_play_patt.configure(style="pressed.TButton")



            #elif message[0] == "Tick:": #queue is too slow for this!
            #    tick = int(message[1])-1
            #    tick_prev = tick-1
            #    if tick_prev == -1:
            #        tick_prev = 15
            #    self.label_tick_nr[tick].configure(style = "tick_active.TLabel")
            #    self.label_tick_nr[tick_prev].configure(style = "default.TLabel")
            #elif message[0] == "Tick_15:":
            #    self.label_tick_nr[15].configure(style = "default.TLabel")

        except queue.Empty:
            pass
        except TclError:
            print("Tcl Error: Cannot update elements.")
        except Exception as e:
            print(f"Unexpected error in check_queue_from_main: {e}")
        finally:
            # Schedule the next check only if the GUI is still running
            if self.mainWin.winfo_exists():
                self.mainWin.after(100, self.check_queue_from_main)


    ###### Helper Functions #####
    def textwindow_insert(self, text):
        "Insert text in text window and scroll to the end"
        self.txt_win.insert(self.end, text)
        self.txt_win.see(self.end)

    def get_instruments_names(self, instruments):
        """ Get the names of instruments and their ports and channels."""
        try:
            for i in range(len(instruments)):
                self.instruments_names.append(instruments[i]["instrument_name"])
                self.instruments_ports.append(instruments[i]["midi_port"])
                self.instruments_channels.append(instruments[i]["midi_channel"])
        except Exception as e:
            text = f"Error retrieving instrument names: {e}!"
            print(text)
            self.textwindow_insert(text)
        text = f"Instruments_names:\n{json.dumps(self.instruments_names)}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main

    def retrieve_instr_data(self, midi_port):
        """ Helper function to get ...
            needed by on_butt_connect and combo_midi_port_bind """
        try:
            for port in self.instruments_ports:
                if port in midi_port:
                    index = self.instruments_ports.index(port)
            self.instrument_sv.set(self.instruments_names[index])
            self.chosen_channel = self.instruments_channels[index]
            self.channel_sv.set(self.chosen_channel)
            #print(self.chosen_channel)
            # get drum_names for comboboxes in pattern editor
            self.chosen_instrument_drum_names = []
            for key in self.instruments[index]:
                self.chosen_instrument_drum_names.append(key)
            del self.chosen_instrument_drum_names[0:3] # remove first 3 keys
            for i in range(8):
               self.combo_drum[i]['values'] = self.chosen_instrument_drum_names
        except Exception as e:
            text = f"Error retrieving instrument names: {e}!"
            print(text)
            self.textwindow_insert(text)

    def get_drum_patterns(self, music_genre):
        """ Get drum patterns and their names from file and send them to main.
            Drum patterns are saved in self.drum_patterns and names are saved in
            self.drum_patterns_names. """
        try:
            self.drum_patterns_module_filename = f"drumppy_patterns/drumppy_patterns_{music_genre}.py"
            patterns_module_name = f"drumppy_patterns.drumppy_patterns_{music_genre}"
            drum_patterns_module = import_module(patterns_module_name)
            self.drum_patterns = drum_patterns_module.drum_patterns
        except Exception as e:
            text = f"Error retrieving drum patterns: {e}!"
            print(text)
            self.textwindow_insert(text)
        try:
            self.drum_patterns_names = []
            for i in range(len(self.drum_patterns)):
                self.drum_patterns_names.append(self.drum_patterns[i][0]["pattern_name"])
        except Exception as e:
            text = f"Error retrieving drum pattern names: {e}!"
            print(text)
            self.textwindow_insert(text)
        text = f"Patterns:\n{patterns_module_name}\n{json.dumps(self.drum_patterns_names)}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main

    def load_drum_pattern(self, pattern, feedback = False):
        """"""
        self.chosen_pattern_name = pattern
        self.pattern_name_sv.set(pattern) # update while playing song
        # Clean pattern
        for i in range(8):
            self.butt_mute[i].configure(style="mute_butt.TButton")
            self.butt_mute_txt_sv[i].set("Mute")
            self.combo_drum_txt_sv[i].set("")
            for j in range(16):
                self.butt_pad[j+i*16].configure(image=self.butt_pad_image_inactive, style="patt_butt_off.TButton")
                self.butt_pad_txt_sv[j+i*16].set("")
        # get instrument name and current drum pattern
        self.chosen_instrument_name = self.instrument_sv.get()
        self.textwindow_insert(f"Chosen Pattern: {self.chosen_pattern_name}\n")
        try:
            for i in range(len(self.drum_patterns)):
                if self.chosen_pattern_name == self.drum_patterns[i][0]["pattern_name"]:
                    self.current_drum_pattern = self.drum_patterns[i]
        except:
            text = "error: pattern not found"
            print(text)
            self.textwindow_insert(text + "\n")
            return
        # get pattern data and send it to main
        steps_2_play = self.current_drum_pattern[0]["steps_2_play"]
        self.combo_t_nr_sv.set(steps_2_play)
        bpm = self.current_drum_pattern[0]["bpm"]
        self.bpm_sv.set(bpm)
        self.label_bpm.config(text=f"BPM: {bpm}")
        self.chosen_channel = self.current_drum_pattern[0]["midi_channel"]
        self.channel_sv.set(self.chosen_channel)
        if feedback:
            text = f"Chosen_pattern:\n{self.chosen_instrument_name}\n{self.chosen_pattern_name}\n{bpm}\n{self.chosen_channel}\n{steps_2_play}"
            self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main
        nr_of_drums = self.current_drum_pattern[0]["nr_of_drums"]
        for i in range(nr_of_drums): # check drum name and mute
            stretch = 1
            self.combo_drum_txt_sv[i].set(self.current_drum_pattern[i+1]["drum_name"])
            if self.current_drum_pattern[i+1]["muted"] == "y":
                self.butt_mute[i].configure(style="muted_butt.TButton")
                self.butt_mute_txt_sv[i].set("Muted")
            for j in range(steps_2_play):
                pad_txt = str(self.current_drum_pattern[i+1][j+1][1])
                if stretch > 1:
                    stretch = stretch - 1
                    self.butt_pad[j+i*16].configure(image=self.butt_pad_image_inactive, style="patt_butt_on_stretch.TButton")
                else:
                    if self.current_drum_pattern[i+1][j+1][0] & 0x01 == 1: # Note on
                        if self.current_drum_pattern[i+1][j+1][0] & 0b0000_1110 != 0: # check roll
                            pad_txt = pad_txt + " R" + str((self.current_drum_pattern[i+1][j+1][0] & 0b0001_1110) >> 1)
                        self.butt_pad[j+i*16].configure(image=self.butt_pad_image_inactive, style="patt_butt_on_no_delay.TButton")
                        if len(self.current_drum_pattern[i+1][j+1]) > 2: # we get different nlen and/or a delay
                            delay = self.current_drum_pattern[i+1][j+1][2]
                            if delay != 0:
                                self.butt_pad[j+i*16].configure(image=self.butt_pad_image_a[delay-1], style="patt_butt_on.TButton")
                        if len(self.current_drum_pattern[i+1][j+1]) > 3: # we get different stretch
                            stretch = self.current_drum_pattern[i+1][j+1][3]
                            print(stretch)
                            self.butt_pad[j+i*16].configure(style="patt_butt_on_stretch.TButton")




                        self.butt_pad_txt_sv[j+i*16].set(pad_txt)
                    else:
                        self.butt_pad[j+i*16].configure(image=self.butt_pad_image_inactive, style="patt_butt_off.TButton")
                        self.butt_pad_txt_sv[j+i*16].set(pad_txt)


        # check lock
        self.lock = self.current_drum_pattern[0]["locked"]
        if self.lock == "n":
            self.butt_lock.configure(text = self.widget_texts_dict["Free"], style="pressed.TButton")
        else:
            self.butt_lock.configure(text = self.widget_texts_dict["Locked"], style="important.TButton")

    def create_text_drum_patterns_list(self):
        text = "drum_patterns = " + json.dumps(self.drum_patterns)
        mtext = text.replace(", ",",")
        mtext = mtext.replace(": ",":")
        mtext = mtext.replace("},","},\n                  ")
        mtext = mtext.replace("}],","}\n                 ],\n                 ")
        mtext = mtext.replace('"1"','1')
        mtext = mtext.replace('"2"','2')
        mtext = mtext.replace('"3"','3')
        mtext = mtext.replace('"4"','4')
        mtext = mtext.replace('"5"','5')
        mtext = mtext.replace('"6"','6')
        mtext = mtext.replace('"7"','7')
        mtext = mtext.replace('"8"','8')
        mtext = mtext.replace('"9"','9')
        mtext = mtext.replace('"10"','10')
        mtext = mtext.replace('"11"','11')
        mtext = mtext.replace('"12"','12')
        mtext = mtext.replace('"13"','13')
        mtext = mtext.replace('"14"','14')
        mtext = mtext.replace('"15"','15')
        mtext = mtext.replace('"16"','16')
        return mtext

    def load_song(self):
        """ Load song """
        # Clean song
        for i in range(4):
            self.combo_song_patt_txt_sv[i].set("")
            self.combo_song_patt_repeat_txt_sv[i].set("")
        self.music_genre_sv.set(self.song[0]["music_genre"]) # update music genre
        self.get_drum_patterns(self.song[0]["music_genre"])
        for i in range(4):
            self.combo_song_patt[i]['values'] = self.drum_patterns_names
        for i in range(len(self.song[1])):
                if self.song[1][i][0] != "":
                    print(self.song[1][i][0])
                    self.combo_song_patt[i].set(self.song[1][i][0])
                    self.combo_song_patt_repeat[i].set(self.song[1][i][1])
        self.butt_seg[0].configure(style="pressed.TButton")
        self.load_drum_pattern(self.song[1][0][0])

    def save_patterns(self):
        """ Save the patterns to a file """
        #self.current_drum_pattern[0]["pattern_name"] = self.chosen_pattern_name
        mtext = self.create_text_drum_patterns_list()
        with open(self.drum_patterns_module_filename, "w") as f:
            f.write(mtext)
            text = 'Pattern is saved!\n'
            self.textwindow_insert(text)



    ###### Functions for Connect frame: Connect to MIDI port ######
    def on_butt_connect(self):
        """ Command connect button (MIDI ports) """
        self.chosen_midi_port = self.midi_port_sv.get()
        self.retrieve_instr_data(self.chosen_midi_port)
        self.midi_port_label_sv.set(self.chosen_midi_port)
        self.textwindow_insert(f"Chosen MIDI Port: {self.chosen_midi_port}\n")
        text = f"Midi_port:\n{self.chosen_midi_port}\n{self.chosen_channel}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main
        self.textwindow_insert(f"{self.widget_texts_dict['Connected']}\n")
        self.butt_connect.configure(style="pressed.TButton",
                                    text=self.widget_texts_dict['Connected'])
        self.load_drum_pattern(self.pattern_name_sv.get(), True)

    def combo_midi_port_bind(self, event):
        """ Binding to combobox MIDI ports """
        self.chosen_midi_port = self.midi_port_sv.get()
        self.retrieve_instr_data(self.chosen_midi_port)

    def on_butt_rescan_midi_ports(self):
        """ Command to rescan MIDI ports if changes because op plugging and
            unplugging cables """
        self.flags_2_main["flag_rescan"].set()  # Set the rescan flag for main
        self.textwindow_insert(f"Rescanning the MIDI ports\n")
        self.butt_connect.configure(style="important.TButton",
                                    text=self.widget_texts_dict['Connected'])

    ###### Functions for Connect frame: Instrument and channel combobox ######
    def combo_instrument_bind(self, event):
        """ Binding to combobox instrument """
        self.chosen_instrument_name = self.instrument_sv.get()
        self.textwindow_insert(f"Instrument changed to: {self.chosen_instrument_name}\n")
        text = f"Instrument change:\n{self.chosen_instrument_name}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def combo_channel_bind(self, event):
        """ Binding to combobox channel """
        self.chosen_channel = self.channel_sv.get()
        self.textwindow_insert(f"Channel changed to: {self.chosen_channel}\n")
        text = f"Channel change:\n{self.chosen_channel}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    ###### Functions for Connect frame: Chose genre and pattern ######
    def combo_genre_bind(self, event):
        chosen_genre = self.music_genre_sv.get()
        self.get_drum_patterns(chosen_genre)
        self.combo_patt['values'] = self.drum_patterns_names
        self.combo_patt.current(0)
        self.textwindow_insert(f"Genre changed to: {chosen_genre}\n")
        text = f"Genre change:\n{chosen_genre}\n{self.drum_patterns_names}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main
        self.load_drum_pattern(self.pattern_name_sv.get(),True)

    def combo_patt_bind(self, event):
        """"""
        self.load_drum_pattern(self.pattern_name_sv.get(),True)

    ###### Functions for Connect frame: Save and Save as ######
    def on_butt_save(self):
        """ Save the pattern """
        if self.lock == "y":
             text = 'This pattern is locked !! Choose "Save as" with a new name or unlock.\n'
             self.textwindow_insert(text)
             return
        else:
            self.current_drum_pattern[0]["pattern_name"] = self.chosen_pattern_name
            self.save_patterns()
            #mtext = self.create_text_drum_patterns_list()
            #with open(self.drum_patterns_module_filename, "w") as f:
            #    f.write(mtext)
            #    text = 'Pattern is saved!\n'
            #    self.textwindow_insert(text)

    def on_butt_save_as(self):
        """ Save the pattern as a new pattern """
        drum_pattern_new = copy.deepcopy(self.current_drum_pattern) # we need deepcopy to avoid shared references!
        drum_pattern_new[0]["pattern_name"] = self.new_pattern_name_sv.get()
        self.drum_patterns.append(drum_pattern_new)
        self.save_patterns()
        #mtext = self.create_text_drum_patterns_list()
        #with open(self.drum_patterns_module_filename, "w") as f:
        #    f.write(mtext)
        #    text = 'New Pattern is saved!\n'
        #    self.textwindow_insert(text)

    ###### Functions for Connect frame: Open song editor and save patt2midi ######
    def on_butt_open_song_editor(self):
        """ Save the song as midi file"""
        if self.song_grid_visible:
            self.frame_Song_editor.grid_remove()
            self.frame_Song_play_save.grid_remove()
            self.song_grid_visible = False
            self.butt_song_editor.configure(text=self.widget_texts_dict["Open_song_editor"], style="important.TButton")
        else:
            self.frame_Song_editor.grid()
            self.frame_Song_play_save.grid()
            self.song_grid_visible = True
            self.butt_song_editor.configure(text=self.widget_texts_dict["Close_song_editor"], style="pressed.TButton")

    def on_butt_save_patt2midi(self):
        """ Save the song as midi file"""
        pass

    ###### Functions pattern editor frame (drum, pad, mute, velocity) ######
    # I didn't find a fast way to pass a variable with the bindings
    def combo_drum_1_bind(self, event):
        """ Binding to combobox drum nr 1 """
        drum_name = self.combo_drum_txt_sv[0].get()
        self.current_drum_pattern[1]["drum_name"] = drum_name

    def combo_drum_2_bind(self, event):
        """ Binding to combobox drum nr 2 """
        drum_name = self.combo_drum_txt_sv[1].get()
        self.current_drum_pattern[2]["drum_name"] = drum_name

    def combo_drum_3_bind(self, event):
        """ Binding to combobox drum nr 3 """
        drum_name = self.combo_drum_txt_sv[2].get()
        self.current_drum_pattern[3]["drum_name"] = drum_name

    def combo_drum_4_bind(self, event):
        """ Binding to combobox drum nr 4 """
        drum_name = self.combo_drum_txt_sv[3].get()
        self.current_drum_pattern[4]["drum_name"] = drum_name

    def combo_drum_5_bind(self, event):
        """ Binding to combobox drum nr 5 """
        drum_name = self.combo_drum_txt_sv[4].get()
        self.current_drum_pattern[5]["drum_name"] = drum_name

    def combo_drum_6_bind(self, event):
        """ Binding to combobox drum nr 6 """
        drum_name = self.combo_drum_txt_sv[5].get()
        self.current_drum_pattern[6]["drum_name"] = drum_name

    def combo_drum_7_bind(self, event):
        """ Binding to combobox drum nr 7 """
        drum_name = self.combo_drum_txt_sv[6].get()
        self.current_drum_pattern[7]["drum_name"] = drum_name

    def combo_drum_8_bind(self, event):
        """ Binding to combobox drum nr 8 """
        drum_name = self.combo_drum_txt_sv[7].get()
        self.current_drum_pattern[8]["drum_name"] = drum_name

    def on_butt_pad(self,nr):
        """ One of 128 pads is pressed """
        drum_nr = (nr//16)+1
        tick_nr = (nr%16)+1
        if self.butt_pad_txt_sv[nr].get() == '':
            self.butt_pad_txt_sv[nr].set(0)
        if self.butt_pad_txt_sv[nr].get() == '0': # we toggle to active
             vel = int(float(self.scale_vel_sv.get()))  # Safely convert to int
             txt = str(vel)
             roll = int(float(self.combo_roll_sv.get()))  # check roll
             delay = int(float(self.combo_delay_sv.get()))  # check delay
             stretch = int(float(self.combo_stretch_sv.get()))  # check stretch
             if roll != 0:
                 note_on = (roll<<1)+1
                 txt = txt + " R" + str(roll)
             else:
                 note_on = 1
             self.current_drum_pattern[drum_nr][tick_nr] = [note_on,vel]
             self.butt_pad[nr].configure(style="patt_butt_on.TButton")
             if delay != 0:
                 self.current_drum_pattern[drum_nr][tick_nr] = [note_on,vel,delay]
                 self.butt_pad[nr].configure(image=self.butt_pad_image_a[delay-1], style="patt_butt_on.TButton")
             else:
                 self.butt_pad[nr].configure(image=self.butt_pad_image_inactive, style="patt_butt_on.TButton")
             if stretch != 0:
                 self.current_drum_pattern[drum_nr][tick_nr] = [note_on,vel,delay,stretch]
                 self.butt_pad[nr].configure(style="patt_butt_on_stretch.TButton")
                 print(self.butt_pad_txt_sv[nr].get())
                 for i in range(1,stretch):
                     self.current_drum_pattern[drum_nr][tick_nr+i] = [0,0]
                     self.butt_pad[nr+i].configure(image=self.butt_pad_image_inactive, style="patt_butt_on_stretch.TButton")
                     self.butt_pad_txt_sv[nr+i].set("")
             #else:
             #     for i in range(1,16):
             #         if self.butt_pad_txt_sv[nr+i].get() == "":
             #             #self.butt_pad[nr+i].configure(style="patt_butt_off.TButton")
             self.butt_pad_txt_sv[nr].set(txt)
        else:
             self.current_drum_pattern[drum_nr][tick_nr] = [0,0]
             self.butt_pad[nr].configure(style="patt_butt_off.TButton")
             self.butt_pad_txt_sv[nr].set(0)
        print(self.current_drum_pattern[1])

    def on_butt_mute(self,nr):
        drum_nr = nr+1
        if self.butt_mute_txt_sv[nr].get() == "Mute":
            self.current_drum_pattern[drum_nr]["muted"] = "y"
            self.butt_mute[nr].configure(style="muted_butt.TButton")
            self.butt_mute_txt_sv[nr].set("Muted")
        else:
            self.current_drum_pattern[drum_nr]["muted"] = "n"
            self.butt_mute[nr].configure(style="mute_butt.TButton")
            self.butt_mute_txt_sv[nr].set("Mute")

    def scale_velocity_bind(self, event):
        vel = int(float(self.scale_vel_sv.get()))  # Safely convert to int
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] + str(vel))
        self.textwindow_insert(f"Velocity change: {vel}\n")

    def velocity_set_1(self):
        """ Set the Velocity to value 1 by pressing a button """
        self.scale_vel_sv.set(self.velocity_1)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_1))
        self.textwindow_insert(f"Velocity change: {self.velocity_1}\n")

    def velocity_set_2(self):
        """ Set the Velocity to value 2 by pressing a button """
        self.scale_vel_sv.set(self.velocity_2)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_2))
        self.textwindow_insert(f"Velocity change: {self.velocity_2}\n")

    def velocity_set_3(self):
        """ Set the Velocity to value 3 by pressing a button """
        self.scale_vel_sv.set(self.velocity_3)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_3))
        self.textwindow_insert(f"Velocity change: {self.velocity_3}\n")

    def combo_t_nr_bind(self, event):
        steps_2_play = self.combo_t_nr_sv.get()
        self.current_drum_pattern[0]["steps_2_play"] = steps_2_play
        text = f"Steps_2_play_change:\n{steps_2_play}"
        self.textwindow_insert(text)
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def on_butt_lock(self):
        """ Toggle lock """
        if self.lock == "n":
            self.lock = "y"
            self.butt_lock.configure(text = self.widget_texts_dict["Locked"], style="important.TButton")
            self.current_drum_pattern[0]["locked"] = self.lock
            self.save_patterns()
        else:
            self.lock = "n"
            self.butt_lock.configure(text = self.widget_texts_dict["Free"], style="pressed.TButton")
        self.current_drum_pattern[0]["locked"] = self.lock
        self.textwindow_insert(f"Lock changed to: {self.lock}\n")

###### Functions play pattern frame (BPM, play, stop) ######
    def on_butt_play_pattern_once(self):
        self.flags_2_main["flag_play_patt_once"].set()
        self.textwindow_insert(f"Playing pattern once\n")
        self.butt_play_patt_once.configure(style="pressed.TButton")

    def on_butt_play_pattern(self):
        self.flags_2_main["flag_play_patt"].set()
        self.textwindow_insert(f"Playing pattern\n")
        self.butt_play_patt.configure(style="pressed.TButton")
        self.butt_stop_play_patt.configure(style="important.TButton")

    def on_butt_stop_playing_pattern(self):
        self.flags_2_main["flag_stop_play_patt"].set()  # Set the exit flag
        self.textwindow_insert(f"Stopped playing pattern\n")
        self.butt_play_patt.configure(style="important.TButton")
        self.butt_stop_play_patt.configure(style="pressed.TButton")

    def scale_bpm_bind(self, event):
        """ this is called when bpm scale changes"""
        bpm = int(float(self.bpm_sv.get()))  # Safely convert to int
        self.label_bpm.config(text=f"BPM: {bpm}")
        if self.current_drum_pattern != []: # not connected
            self.current_drum_pattern[0]["bpm"] = bpm # save to pattern
            text = f"BPM change: {bpm}\n"
            self.queue_2_main.put(f"BPM change:\n{bpm}")  # Add the text to queue_2_main flag is set in main
        else:
            text = "No valid midi port! Connect first!\n"
        self.textwindow_insert(text)

    def on_butt_bpm_set(self, nr):
        """ Set the BPM to a value by pressing a button """
        self.bpm_sv.set(self.bpm[nr])
        self.label_bpm.config(text=f"BPM: {self.bpm[nr]}")
        if self.current_drum_pattern != []: # not connected
            self.current_drum_pattern[0]["bpm"] = self.bpm[nr] # save to pattern
            text = f"BPM change: {self.bpm[nr]}\n"
            self.queue_2_main.put(f"BPM change:\n{self.bpm[nr]}")  # Add the text to queue_2_main flag is set in main
        else:
            text = "No valid midi port! Connect first!\n"
        self.textwindow_insert(text)

    ###### Functions song editor ######
    def on_butt_seg(self,nr):
        pass

    def combo_song_patt_1_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_1_repeat_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_2_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_2_repeat_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_3_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_3_repeat_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_4_bind(self, event):
        """ Binding to combobox repeat """
        pass
    def combo_song_patt_4_repeat_bind(self, event):
        """ Binding to combobox repeat """
        pass

    ###### Functions play save pattern frame ######

    def on_butt_play_song(self):
        """Function to play a song of patterns."""
        try:
            self.load_drum_pattern(self.song[1][0][0])
        except:
            text = "No song loaded"
            print(text)
            self.textwindow_insert(text)
        self.flags_2_main["flag_play_song"].set()  # Set the flag
        self.textwindow_insert(f"Playing song\n")
        self.butt_play_song.configure(style="pressed.TButton")
        self.butt_stop_play_song.configure(style="important.TButton")


    def on_butt_stop_playing_song(self):
        self.flags_2_main["flag_stop_play_song"].set()  # Set the exit flag
        self.textwindow_insert(f"Stopped playing song\n")
        self.butt_play_song.configure(style="important.TButton")
        self.butt_stop_play_song.configure(style="pressed.TButton")

    def on_butt_open_song_file(self):
        """ Get song file """
        os.chdir("drumppy_songs")  # Change to the drumppy_songs directory
        try:
            filename = fd.askopenfilename(title="Open song file",
                                          filetypes=(("Drumppy song files", "*.dsong.py"),
                                                     ("All files", "*.*")))
        except Exception as e:
            self.textwindow_insert(f"Error opening song file: {e}\n")
            return
        if filename:
            self.textwindow_insert(f"Song file opened: {filename}\n")
        else:
            self.textwindow_insert("No song file selected.\n")
        with open(filename, "r") as f:
            song = f.read()
        self.queue_2_main.put(f"Song_loaded:\n{song}")
        self.song = json.loads(song)
        self.song_name = self.song[0]["song_name"]
        self.song_genre = self.song[0]["music_genre"]
        self.song_bpm = self.song[0]["bpm"]
        text = f"Opened song {self.song_name}, music genre: {self.song_genre}, bpm: {self.song_bpm}"
        print(text)
        self.textwindow_insert(text)
        os.chdir("..")  # Change back to the original directory
        self.load_song()

    def on_butt_save_song(self):
        """ Save the song """
        self.frame_Song_editor.grid()
        with open(f"drumppy_songs/{self.song_name}.dsong.py", "w") as f:

            f.write(json.dumps(self.song, indent=4))
            text = 'Song is saved!\n'
            self.textwindow_insert(text)

    def on_butt_save_midifile(self):
        """ Save the song as midi file"""
        if self.song_grid_visible:
            self.frame_Song_editor.grid_remove()
            self.song_grid_visible = False
        else:
            self.frame_Song_editor.grid()
            self.song_grid_visible = True
        #self.flags_2_main["flag_save_midifile"].set()
        text = 'Song is saved!\n'
        self.textwindow_insert(text)





    ###### Functions to clear textwindow and close ######
    def clear_textwindow(self):
        self.txt_win.delete(1.0, self.end)

    def on_close(self):
        """Handle GUI close event"""
        self.flags_2_main["flag_stop_play_patt"].set()  # Set the exit flag
        sleep(0.5)
        self.flags_2_main["flag_exit"].set()  # Set the exit flag
        self.mainWin.destroy()  # Close the GUI window

    def init_ttk_styles(self):
        self.s = ttk.Style()
        #frames
        self.s.configure("all.TFrame",
                         background="lightgrey")
        self.s.configure("test.TFrame",
                         background="grey")
        #widgets
        self.s.configure("default.TLabel",
                         background="lightgrey",
                         font=self.standard_font)
        self.s.configure("default_big.TLabel",
                         background="lightgrey",
                         foreground="red",
                         font=self.standard_font_big)
        self.s.configure("tick_active.TLabel",
                         background="red",
                         font=self.standard_font)
        self.s.configure("time.TLabel",
                         background="lightgrey",
                         font=self.standard_font)
        self.s.configure("default.TEntry",
                         background="lightgray",
                         font=self.standard_font)
        self.s.configure("default.TCombobox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("highligted.TCombobox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lawngreen",
                         arrowsize=20)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("important.TButton",
                         background="orangered",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("default.TButton",
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5,
                         height = 10)
        self.s.configure("pressed.TButton",          # New style for pressed button
                         background="lawngreen",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("patt_butt_inactive.TButton",          # New style for pressed button
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw",
                         image = self.butt_pad_image_inactive,
                         compound = BOTTOM)
        self.s.configure("patt_butt_on_no_delay.TButton",          # New style for pressed button
                         background="red",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw",
                         image = self.butt_pad_image_inactive,
                         compound = BOTTOM)
        self.s.configure("patt_butt_on.TButton",          # New style for pressed button
                         background="red",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw",
                         image = self.butt_pad_image,
                         compound = BOTTOM)
        self.s.configure("patt_butt_on_stretch.TButton",          # New style for pressed button
                         background="darkorange",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw",
                         image = self.butt_pad_image,
                         compound = BOTTOM)
        self.s.configure("patt_butt_off.TButton",          # New style for pressed button
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw",
                         image = self.butt_pad_image_inactive,
                         compound = BOTTOM)
        self.s.configure("mute_butt.TButton",          # New style for pressed button
                         background="lightgrey",
                         font=self.standard_font_small,
                         justify="center")
        self.s.configure("muted_butt.TButton",          # New style for pressed button
                         background="orange",
                         font=self.standard_font_small,
                         justify="center")
        self.s.configure("velocity.TButton",          # New style for pressed button
                         background="lightgrey",
                         font=self.standard_font,
                         justify="center")
        self.s.configure("default.Horizontal.TScale",          # New style for pressed button
                         #background="red",
                         sliderlength=50,
                         )

        self.s.map("important.TButton",
                   background = [("active", 'orangered')])
        self.s.map("pressed.TButton",
                   background = [("active", 'lawngreen')])
        self.s.map("muted_butt.TButton",
                   background = [("active", 'orange')])
        self.s.map("patt_butt_on.TButton",
                   background = [("active", 'red')])
        self.s.map("patt_butt_off.TButton",
                   background = [("active", 'lightgrey')])

    def FontSizeUpdate(self):
        FSize = self.FSize_sv.get()
        self.standard_font[1]=int(FSize)
        self.textbox_font[1]=int(FSize)
        print(self.standard_font)
        self.s.configure("default.TLabel", font=self.standard_font)
        self.s.configure("default_big.TLabel", font=self.standard_font_big)
        self.s.configure("time.TLabel", font=self.standard_font)
        self.s.configure("default.TEntry", font=self.standard_font)
        self.s.configure("default.TButton", font=self.standard_font)
        self.s.configure("important.TButton", font=self.standard_font)
        self.s.configure("pressed.TButton", font=self.standard_font)
        self.s.configure("default.TCombobox", font=self.standard_font)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=int(FSize)*1.5)
        self.txt_win.config(font=self.textbox_font)
        self.combo_hpdir.config(font=self.standard_font)
        self.combo_quick_links.config(font=self.standard_font)
        self.combo_check_links.config(font=self.standard_font)
        self.spinb_fontsize.config(font=self.standard_font)

    def UpdateTime(self):
        ftime = strftime("%d.%m.%y %H:%M:%S", localtime())
        rtctime = strftime("%Y %m %d %H %M %S", localtime())
        intyear = str(int(rtctime[0:4])-1892)
        rtctimecorr = intyear[0:4]+rtctime[4:]
        self.label_time['text'] = ftime
        self.label_time.after(1000, self.UpdateTime)

    def run(self):
        self.mainWin = Tk()
        self.image_title = PhotoImage(file='png_xbm/drumppy.png')
        self.butt_pad_image_inactive = BitmapImage(file='png_xbm/butt_pad_1_16.xbm', foreground='alpha')
        self.butt_pad_image_a = []
        for i in range(1,16):
            self.butt_pad_image_a.append(BitmapImage(file=f"png_xbm/butt_pad_{i}_16.xbm", foreground='white'))
        self.butt_pad_image = self.butt_pad_image_a[0]
        self.init_ttk_styles()
        self.get_drum_patterns(self.music_genres[0])
        self.get_instruments_names(instruments)
        self.FSize_sv = StringVar()
        self.FSize_sv.set("12")
        self.midi_port_sv = StringVar()
        self.midi_port_sv.set("")
        self.midi_port_label_sv = StringVar()
        self.midi_port_label_sv.set("")
        self.instrument_sv = StringVar()
        self.instrument_sv.set(self.instruments_names[0])
        self.music_genre_sv = StringVar()
        self.music_genre_sv.set(self.music_genres[0])
        self.pattern_name_sv = StringVar()
        self.pattern_name_sv.set(self.drum_patterns_names[0])
        self.channel_sv = StringVar()
        self.channel_sv.set(10)
        self.new_pattern_name_sv = StringVar()
        self.new_pattern_name_sv.set(f"basic_{self.music_genre_sv.get()}_1")
        self.butt_pad_txt_sv = []
        for i in range(128):
            var = StringVar()
            var.set("")
            self.butt_pad_txt_sv.append(var)
        self.combo_drum_txt_sv = []
        for i in range(8):
            var = StringVar()
            var.set("")
            self.combo_drum_txt_sv.append(var)
        self.butt_mute_txt_sv = []
        for i in range(8):
            var = StringVar()
            var.set("Mute")
            self.butt_mute_txt_sv.append(var)
        self.scale_vel_sv = StringVar()
        self.scale_vel_sv.set("64")
        self.butt_seg_txt_sv = []
        for i in range(16):
            var = StringVar()
            var.set("Seg" + str(i+1))
            self.butt_seg_txt_sv.append(var)
        self.combo_roll_sv = StringVar()
        self.combo_roll_sv.set(0)
        self.combo_stretch_sv = StringVar()
        self.combo_stretch_sv.set(0)
        self.combo_delay_sv = StringVar()
        self.combo_delay_sv.set(0)
        self.combo_t_nr_sv = StringVar()
        self.combo_t_nr_sv.set(16)
        self.combo_song_patt_txt_sv = []
        for i in range(4):
            var = StringVar()
            var.set("")
            self.combo_song_patt_txt_sv.append(var)
        self.combo_song_patt_repeat_txt_sv = []
        for i in range(4):
            var = StringVar()
            var.set(1)
            self.combo_song_patt_repeat_txt_sv.append(var)
        self.bpm_sv = StringVar()
        self.bpm_sv.set("120")
        self.mainWin.protocol("WM_DELETE_WINDOW", self.on_close)
        self.mainWin.after(100, self.check_queue_from_main)  # Periodically check GUI queue
        self.mainWin.title(self.widget_texts_dict["Title"])
        self.mainWin.columnconfigure(0, weight=1)
        self.mainWin.rowconfigure(0, weight=1)
        #++++++ Frame MAIN +++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Main = ttk.Frame(self.mainWin,
                                    borderwidth=10,
                                    relief='ridge',
                                    padding="5 5 10 10",
                                    style = "all.TFrame")
        self.frame_Main.grid(column=0, row=0, sticky=(W, N, E, S))
        for column in range(1,3): # 2 columns
            self.frame_Main.columnconfigure(column, weight=1)
        for row in range(1,6):    # 5 rows
            self.frame_Main.rowconfigure(row, weight=1)
        #++++++ Frame Header: Image with time and fontsize spinbox +++++++++++
        self.frame_Header = ttk.Frame(self.frame_Main,
                                      borderwidth=3,
                                      relief='groove',
                                      padding="5 5 10 10",
                                      style="all.TFrame")
        self.frame_Header.grid(column=1, row=1, columnspan=2, sticky=(N,W,E))
        for column in range(1,3): # 2 columns
            self.frame_Header.columnconfigure(column, weight=1)
        for row in range(1,2):    # 1 rows
            self.frame_Header.rowconfigure(row, weight=1)
        self.label_png = ttk.Label(self.frame_Header, text="",
                                   image=self.image_title,
                                   style="default.TLabel")
        self.label_png.grid(column=1, row=1, columnspan=3, sticky=N)
        self.frame_Time_Font = ttk.Frame(self.frame_Header, style="all.TFrame")
        self.frame_Time_Font.grid(column=2, row=1, sticky=(E,N))

        self.label_time = ttk.Label(self.frame_Time_Font, text="",
                                    justify='right',
                                    style="time.TLabel")
        self.label_time.grid(ipady=self.ipady, column=1, row=1, sticky=(N,E))
        self.frame_Fontsize = ttk.Frame(self.frame_Time_Font, style="all.TFrame")
        self.frame_Fontsize.grid(column=1, row=2, sticky=(E,N))
        self.label_fontsize = ttk.Label(self.frame_Fontsize,
                                        text="Fontsize: ",
                                        style="default.TLabel")
        self.label_fontsize.grid(column=1, row=1,sticky=(E))
        self.spinb_fontsize = ttk.Spinbox(self.frame_Fontsize,from_=6, to=24,
                                          textvariable=self.FSize_sv,
                                          command=self.FontSizeUpdate, width=4,
                                          justify='center',
                                          font=self.standard_font,
                                          style="default.TSpinbox")
        self.spinb_fontsize.grid(column=2, row=1, sticky=(E))
        #++++++ Frame Connect ++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Connect = ttk.Frame(self.frame_Main,
                                       borderwidth=3,
                                       relief='groove',
                                       padding="5 5 10 10",
                                       style = "all.TFrame")
        self.frame_Connect.grid(column=1, row=2, columnspan = 5, sticky=(W,E))
        for column in range(1,7):
            self.frame_Connect.columnconfigure(column, weight=1)
        for row in range(1,7):
            self.frame_Connect.rowconfigure(row, weight=1)
        #------ Frame Midi port ----------------------------------------------
        self.frame_Midi_port = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Midi_port.grid(column=1, row=1, sticky=(N))
        for row in range(1,6):
            self.frame_Midi_port.rowconfigure(row, weight=1)
        self.butt_connect = ttk.Button(self.frame_Midi_port,
                                       text=self.widget_texts_dict["Connect"],
                                       command=self.on_butt_connect,
                                       width=self.button_width_big,
                                       style="important.TButton")
        self.butt_connect.grid(ipady=self.ipady, column=1,row=1,sticky=(W))
        self.label_midi_port = ttk.Label(self.frame_Midi_port,
                                         text=self.widget_texts_dict["Midi_ports"],

                                         foreground="red",
                                         style="default.TLabel")
        self.label_midi_port.grid(pady = (10,0), column=1, row=2, sticky=(N,W,E))
        self.combo_midi_port = ttk.Combobox(self.frame_Midi_port,
                                              width=self.button_width_big,
                                              textvariable=self.midi_port_sv,
                                              font=self.standard_font,
                                              style="default.TCombobox")
        self.combo_midi_port.grid(pady = 5, ipady=self.ipady, column=1, row=3, sticky=(S,W))
        self.combo_midi_port['values'] = self.midi_port_names
        self.combo_midi_port.current()
        self.combo_midi_port.bind("<<ComboboxSelected>>", self.combo_midi_port_bind)
        self.label_chosen_port_1 = ttk.Label(self.frame_Midi_port,
                                             text=self.widget_texts_dict["Chosen_port"],
                                             foreground="red",
                                             style="default.TLabel")
        self.label_chosen_port_1.grid(pady = (0,0), column=1, row=4, sticky=(N,W,E))
        self.label_chosen_port_2 = ttk.Label(self.frame_Midi_port,
                                             textvariable=self.midi_port_label_sv,
                                             style="default.TLabel")
        self.label_chosen_port_2.grid(pady = (5,0), column=1, row=5, sticky=(N,W,E))
        #------ Frame Instruments, Channels ----------------------------------
        self.frame_Instruments = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Instruments.grid(column=2, row=1, sticky=(N))
        for row in range(1,6):
            self.frame_Instruments.rowconfigure(row, weight=1)
        self.butt_rescan = ttk.Button(self.frame_Instruments,
                                      text=self.widget_texts_dict["Rescan"],
                                      command=self.on_butt_rescan_midi_ports,
                                      width=self.button_width,
                                      style="default.TButton")
        self.butt_rescan.grid(ipady=self.ipady, column=1,row=1, sticky=(W))
        self.label_instr = ttk.Label(self.frame_Instruments,
                                         text=self.widget_texts_dict["Instruments"],
                                         foreground="red",
                                         style="default.TLabel")
        self.label_instr.grid(pady = (10,0), column=1, row=2, sticky=(N,W,E))
        self.combo_instr = ttk.Combobox(self.frame_Instruments,
                                              width=self.button_width,
                                              textvariable=self.instrument_sv,
                                              font=self.standard_font,
                                              style="default.TCombobox")
        self.combo_instr.grid(pady = (0,0), ipady=self.ipady, column=1, row=3, sticky=(S,W))
        self.combo_instr['values'] = self.instruments_names
        self.combo_instr.current()
        self.combo_instr.bind("<<ComboboxSelected>>", self.combo_instrument_bind)
        self.label_channel = ttk.Label(self.frame_Instruments,
                                         text=self.widget_texts_dict["Channels"],
                                         foreground="red",
                                         style="default.TLabel")
        self.label_channel.grid(pady = (5,0), column=1, row=5, sticky=(N,W,E))
        self.combo_channel = ttk.Combobox(self.frame_Instruments,
                                             width=self.button_width,
                                             textvariable=self.channel_sv,
                                             font=self.standard_font,
                                             style="default.TCombobox")
        self.combo_channel.grid(pady = 0, ipady=self.ipady, column=1, row=6, sticky=(S,W))
        self.combo_channel['values'] = [str(i) for i in range(1, 17)]  # MIDI channels 1-16
        self.combo_channel.current()
        self.combo_channel.bind("<<ComboboxSelected>>", self.combo_channel_bind)
        #------ Frame Patterns -----------------------------------------------
        self.frame_Patterns = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Patterns.grid(column=3, row=1, sticky=(N))
        for row in range(1,6):
            self.frame_Patterns.rowconfigure(row, weight=1)
        self.label_genre = ttk.Label(self.frame_Patterns,
                                     text=self.widget_texts_dict["Genre"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_genre.grid(pady = (10,0), column=1, row=2, sticky=(N,W,E))
        self.combo_genre = ttk.Combobox(self.frame_Patterns,
                                       width=self.button_width,
                                       textvariable=self.music_genre_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_genre.grid(pady = 5, ipady=self.ipady, column=1, row=3, sticky=(S,W))
        self.combo_genre['values'] = self.music_genres
        self.combo_genre.current(0)
        self.combo_genre.bind("<<ComboboxSelected>>", self.combo_genre_bind)
        self.label_patt = ttk.Label(self.frame_Patterns,
                                    text=self.widget_texts_dict["Patterns"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_patt.grid(pady = (10,0), column=1, row=4, sticky=(N,W,E))
        self.combo_patt = ttk.Combobox(self.frame_Patterns,
                                       width=self.button_width,
                                       textvariable=self.pattern_name_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_patt.grid(pady = 5, ipady=self.ipady, column=1, row=5, sticky=(S,W))
        self.combo_patt['values'] = self.drum_patterns_names
        self.combo_patt.current(0)
        self.combo_patt.bind("<<ComboboxSelected>>", self.combo_patt_bind)
        #------ Frame Save patterns ------------------------------------------
        self.frame_Save_p = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Save_p.grid(column=4, row=1, sticky=(N))
        for row in range(1,6):
            self.frame_Save_p.rowconfigure(row, weight=1)
        self.butt_save = ttk.Button(self.frame_Save_p,
                                    text=self.widget_texts_dict["Save_pattern"],
                                    command=self.on_butt_save,
                                    width=self.button_width,
                                    style="default.TButton")
        self.butt_save.grid(ipady=self.ipady, column=1,row=1,sticky=(W))
        self.butt_save_p2m = ttk.Button(self.frame_Save_p,
                                        text=self.widget_texts_dict["save_patt_2_midi"],
                                        command=self.on_butt_save_patt2midi,
                                        width=self.button_width,
                                        style="default.TButton")
        self.butt_save_p2m.grid(pady = (10,0), ipady=self.ipady, column=1,row=2,sticky=(W))
        self.butt_save_new_patt = ttk.Button(self.frame_Save_p,
                                        text=self.widget_texts_dict["Save_new_pattern"],
                                        command=self.on_butt_save_as,
                                        width=self.button_width,
                                        style="default.TButton")
        self.butt_save_new_patt.grid(pady = (10,0), ipady=self.ipady, column=1,row=3,sticky=(W))


        #------ Frame open song editor save pattern midi file--------------------
        self.frame_Open_song_editor = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Open_song_editor.grid(column=5, row=1, sticky=(N))
        for row in range(1,6):
            self.frame_Open_song_editor.rowconfigure(row, weight=1)

        self.frame_Open_se = ttk.Frame(self.frame_Open_song_editor, style="all.TFrame")
        self.frame_Open_se.grid(column=1, row=1, sticky=(W,E))
        self.butt_song_editor = ttk.Button(self.frame_Open_se,
                                        text=self.widget_texts_dict["Open_song_editor"],
                                        command=self.on_butt_open_song_editor,
                                        width=self.button_width,
                                        style="important.TButton")
        self.butt_song_editor.grid(ipady=self.ipady, column=1,row=1,sticky=(W))

        self.frame_Save_new = ttk.Frame(self.frame_Open_song_editor, style="all.TFrame")
        self.frame_Save_new.grid(pady = (60,0), column=1, row=2, sticky=(W,E))
        self.label_entry_np = ttk.Label(self.frame_Save_new,
                                        text=self.widget_texts_dict["New_pattern"],
                                        foreground="red",
                                        style="default.TLabel")
        self.label_entry_np.grid(column=1, row=3, sticky=(N,W,E))
        self.entry_save_new = ttk.Entry(self.frame_Save_new,
                                        textvariable=self.new_pattern_name_sv,
                                        width=self.button_width+7,
                                        style="default.TEntry")
        self.entry_save_new.grid(ipady=self.ipady, column=1,row=4,sticky=(W))

        #++++++ Frame Pattern_editor  ++++++++++++++++++++++++++++++++++++++++
        self.frame_Patt_editor = ttk.Frame(self.frame_Main,
                                           borderwidth=3,
                                           relief='groove',
                                           padding="5 5 10 10",
                                           style = "all.TFrame")
        self.frame_Patt_editor.grid(column=1, row=3, columnspan=2,  sticky=(W,E))
        for column in range(1,19): # 18 columns
            self.frame_Patt_editor.columnconfigure(column, weight=10)
        for row in range(1,10):    # 9 rows
            self.frame_Patt_editor.rowconfigure(row, weight=10)
        self.label_patt_editor = ttk.Label(self.frame_Patt_editor,
                                           text=self.widget_texts_dict["Pattern_editor"],
                                           foreground="red",
                                           style="default.TLabel")
        self.label_patt_editor.grid(pady = (10,0), column=1, row=1, sticky=(N,W,E))
        self.label_tick_nr = []
        for i in range(16):
            self.label_tick_nr.append(ttk.Label(self.frame_Patt_editor,
                                      text=str(i+1),
                                      foreground="red",
                                      width = self.butt_pad_width,
                                      anchor="center",
                                      style="default.TLabel"))
            self.label_tick_nr[i].grid(pady = (10,0), column=i+3, row=1, sticky=(N,W,E))

        self.combo_drum = []
        for i in range(8):
            self.combo_drum.append(ttk.Combobox(self.frame_Patt_editor,
                                                width=self.combo_drum_width,
                                                textvariable=self.combo_drum_txt_sv[i],
                                                font=self.standard_font,
                                                style="default.TCombobox"))
        for i in range(8):
            self.combo_drum[i].grid(pady = 10, ipady=self.ipady, column=1, row=i+2, sticky=(S,W))
            self.combo_drum[i]['values'] = self.chosen_instrument_drum_names
            self.combo_drum[i].current()
            if i == 0:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_1_bind)
            elif i == 1:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_2_bind)
            elif i == 2:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_3_bind)
            elif i == 3:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_4_bind)
            elif i == 4:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_5_bind)
            elif i == 5:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_6_bind)
            elif i == 6:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_7_bind)
            elif i == 7:
                self.combo_drum[i].bind("<<ComboboxSelected>>", self.combo_drum_8_bind)

        self.butt_mute = []
        for i in range(8):
            self.butt_mute.append(ttk.Button(self.frame_Patt_editor,
                                             textvariable = self.butt_mute_txt_sv[i],
                                             command=partial(self.on_butt_mute, i),
                                             width=self.butt_mute_width,
                                             style="mute_butt.TButton"))
            self.butt_mute[i].grid(pady = 10, padx = 10, ipady=self.ipady, column=2, row=i+2, sticky=(S,W))

        self.butt_pad = []
        for i in range(128):
            self.butt_pad.append(ttk.Button(self.frame_Patt_editor,
                                            textvariable=self.butt_pad_txt_sv[i],
                                            command=partial(self.on_butt_pad, i),
                                            width=self.butt_pad_width,
                                            style="patt_butt_inactive.TButton"))
        for i in range(16):
            self.butt_pad[i].grid(ipady=1, column=i+3, row=2, sticky=(W,E))
            self.butt_pad[i+16].grid(ipady=1, column=i+3, row=3, sticky=(W,E))
            self.butt_pad[i+32].grid(ipady=1, column=i+3, row=4, sticky=(W,E))
            self.butt_pad[i+48].grid(ipady=1, column=i+3, row=5, sticky=(W,E))
            self.butt_pad[i+64].grid(ipady=1, column=i+3, row=6, sticky=(W,E))
            self.butt_pad[i+80].grid(ipady=1, column=i+3, row=7, sticky=(W,E))
            self.butt_pad[i+96].grid(ipady=1, column=i+3, row=8, sticky=(W,E))
            self.butt_pad[i+112].grid(ipady=1, column=i+3, row=9, sticky=(W,E))
        self.frame_velocity = ttk.Frame(self.frame_Patt_editor,
                                        style = "all.TFrame")
        self.frame_velocity.grid(column=1, row=10, columnspan=2,  sticky=(W,S))
        self.label_velocity = ttk.Label(self.frame_velocity,
                                        text=self.widget_texts_dict["Velocity"] + "64",
                                        foreground="red",
                                        style="default.TLabel")
        self.label_velocity.grid(pady = (10,0), column=1, row=1, sticky=(N,W,E))
        self.scale_velocity = ttk.Scale(self.frame_velocity,
                                   from_= 0,
                                   to=127,
                                   length=self.combo_drum_width*16,
                                   variable=self.scale_vel_sv,
                                   style="default.Horizontal.TScale"
                                  )
        self.scale_velocity.grid(ipady=self.ipady, column=1, row=2, columnspan = 2, sticky=(W,S))
        self.scale_velocity.bind("<ButtonRelease-1>", self.scale_velocity_bind)
        self.butt_vel_1 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_1,
                                     command=self.velocity_set_1,
                                     width=self.butt_pad_width+1,
                                     style="velocity.TButton")
        self.butt_vel_1.grid(ipady=self.ipady, column=3, row=10, sticky=(W,S))
        self.butt_vel_2 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_2,
                                     command=self.velocity_set_2,
                                     width=self.butt_pad_width+1,
                                     style="velocity.TButton")
        self.butt_vel_2.grid(ipady=self.ipady, column=4, row=10, sticky=(W,S))
        self.butt_vel_3 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_3,
                                     command=self.velocity_set_3,
                                     width=self.butt_pad_width+1,
                                     style="velocity.TButton")
        self.butt_vel_3.grid(ipady=self.ipady, column=5, row=10, sticky=(W,S))

        self.frame_Roll = ttk.Frame(self.frame_Patt_editor,
                                    style = "all.TFrame")
        self.frame_Roll.grid(pady = (10,0), column=6, columnspan = 3, row=10,  sticky=(E))

        self.label_roll = ttk.Label(self.frame_Roll,
                                    text=self.widget_texts_dict["Roll"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_roll.grid(padx = (0,10), column=1, row=1, sticky=(W,E))
        self.combo_roll = ttk.Combobox(self.frame_Roll,
                                       width=self.combo_repeat_width,
                                       textvariable=self.combo_roll_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_roll.grid(ipady=self.ipady, column=2, row=1, sticky=(W,E))
        self.combo_roll['values'] = [0,2,3,4,5,6,7]
        self.combo_roll.current()

        self.frame_Delay = ttk.Frame(self.frame_Patt_editor,
                                    style = "all.TFrame")
        self.frame_Delay.grid(pady = (10,0), column=9, columnspan = 3, row=10,  sticky=(E))
        self.label_delay = ttk.Label(self.frame_Delay,
                                    text=self.widget_texts_dict["Delay"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_delay.grid(padx = (0,10), column=1, row=1, sticky=(W,E))
        self.combo_delay = ttk.Combobox(self.frame_Delay,
                                       width=self.combo_repeat_width,
                                       textvariable=self.combo_delay_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_delay.grid(ipady=self.ipady, column=2, row=1, sticky=(W,E))
        self.combo_delay['values'] = [str(i) for i in range(0, 16)]
        self.combo_delay.current()

        self.frame_Stretch = ttk.Frame(self.frame_Patt_editor,
                                    style = "all.TFrame")
        self.frame_Stretch.grid(pady = (10,0), column=12, columnspan = 3, row=10,  sticky=(E))

        self.label_stretch = ttk.Label(self.frame_Stretch,
                                    text=self.widget_texts_dict["Stretch"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_stretch.grid(padx = (0,10), column=1, row=1, sticky=(W,E))
        self.combo_stretch = ttk.Combobox(self.frame_Stretch,
                                       width=self.combo_repeat_width,
                                       textvariable=self.combo_stretch_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_stretch.grid(ipady=self.ipady, column=2, row=1, sticky=(W,E))
        self.combo_stretch['values'] = [0,2,3,4,5,6,7,8]
        self.combo_stretch.current()

        self.frame_T_nr = ttk.Frame(self.frame_Patt_editor,
                                    style = "all.TFrame")
        self.frame_T_nr.grid(pady = (10,0), column=15, columnspan = 3, row=10,  sticky=(E))
        self.label_t_nr = ttk.Label(self.frame_T_nr,
                                    text=self.widget_texts_dict["Tick_nr"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_t_nr.grid(padx = (0,10), column=1, row=1, sticky=(W,E))
        self.combo_t_nr = ttk.Combobox(self.frame_T_nr,
                                       width=self.combo_repeat_width,
                                       textvariable=self.combo_t_nr_sv,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_t_nr.grid(ipady=self.ipady, column=2, row=1, sticky=(W,E))
        self.combo_t_nr['values'] = [str(i) for i in range(1, 17)]
        self.combo_t_nr.current()
        self.combo_t_nr.bind("<<ComboboxSelected>>", self.combo_t_nr_bind)

        self.frame_Lock = ttk.Frame(self.frame_Patt_editor,
                                    style = "all.TFrame")
        self.frame_Lock.grid(pady = (10,0), padx = (10,0), column=18, row=10,  sticky=(E))
        self.butt_lock = ttk.Button(self.frame_Lock,
                                    text="",
                                    command=self.on_butt_lock,
                                    width=self.butt_pad_width,
                                    style="default.TButton")
        self.butt_lock.grid(ipady=self.ipady, column=1, row=1, sticky=(W,E))




        # frame Play  ++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Patt_play = ttk.Frame(self.frame_Main,
                                    borderwidth=3,
                                    relief='groove',
                                    padding="5 5 10 10",
                                    style = "all.TFrame")
        self.frame_Patt_play.grid(column=1, row=4, columnspan=3,  sticky=(W,E))
        for column in range(1,4): # 3 columns
            self.frame_Patt_play.columnconfigure(column, weight=1)
        for row in range(1,3):    # 1 rows
            self.frame_Patt_play.rowconfigure(row, weight=1)

        self.frame_Patt_play_patt_butt = ttk.Frame(self.frame_Patt_play,
                                         style = "all.TFrame")
        self.frame_Patt_play_patt_butt.grid(pady = 0, column=1, row=1, sticky=(W))
        self.butt_play_patt_once = ttk.Button(self.frame_Patt_play_patt_butt,
                                         text=self.widget_texts_dict["Play_pattern_once"],
                                         command=self.on_butt_play_pattern_once,
                                         width=self.button_width_small,
                                         style="important.TButton")
        self.butt_play_patt_once.grid(ipady=self.ipady, column=1, row=1, sticky=(W))
        self.butt_play_patt = ttk.Button(self.frame_Patt_play_patt_butt,
                                         text=self.widget_texts_dict["Play_pattern"],
                                         command=self.on_butt_play_pattern,
                                         width=self.button_width_small,
                                         style="important.TButton")
        self.butt_play_patt.grid(ipady=self.ipady, column=2, row=1, sticky=(W))
        self.butt_stop_play_patt = ttk.Button(self.frame_Patt_play_patt_butt,
                                              text=self.widget_texts_dict["Stop_playing_pattern"],
                                              command=self.on_butt_stop_playing_pattern,
                                              width=self.button_width_small,
                                              style="pressed.TButton")
        self.butt_stop_play_patt.grid(ipady=self.ipady, column=3, row=1, sticky=(W))

        self.frame_Bpm = ttk.Frame(self.frame_Patt_play,
                                   style = "all.TFrame")
        self.frame_Bpm.grid(pady = 0, column=2, row=1, sticky=(W,E))
        self.label_bpm = ttk.Label(self.frame_Bpm,
                                           text=f"BPM: {self.bpm_sv.get()}",
                                           foreground="red",
                                           style="default.TLabel")
        self.label_bpm.grid(column=1, row=1, sticky=(N,W,E))
        self.scale_bpm = ttk.Scale(self.frame_Bpm,
                                   from_= 20,
                                   to=240,
                                   length=self.combo_drum_width*14,
                                   variable = self.bpm_sv,
                                   style="default.Horizontal.TScale")
        self.scale_bpm.grid(padx = (0,10), ipady=self.ipady, column=1, row=2, sticky=(W,S))
        self.scale_bpm.bind("<ButtonRelease-1>", self.scale_bpm_bind)
        self.butt_bpm = []
        for i in range(6):
            self.butt_bpm.append(ttk.Button(self.frame_Bpm,
                                            text=self.bpm[i],
                                            command=partial(self.on_butt_bpm_set, i),
                                            width=self.butt_pad_width+1,
                                            style="velocity.TButton"))
            self.butt_bpm[i].grid(ipady=self.ipady, column=2+i, row=1, rowspan = 2, sticky=(W,S))

        # Frame Song editor  +++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Song_editor = ttk.Frame(self.frame_Main,
                                    borderwidth=3,
                                    relief='groove',
                                    padding="5 5 10 10",
                                    style = "all.TFrame")
        self.frame_Song_editor.grid(column=1, row=5, columnspan=5,  sticky=(W,E))
        for column in range(1,19): # 17 columns
            self.frame_Song_editor.columnconfigure(column, weight=1)
        for row in range(1,4):     # 3 rows
            self.frame_Song_editor.rowconfigure(row, weight=1)

        self.label_song_editor = ttk.Label(self.frame_Song_editor,
                                           text=self.widget_texts_dict["Song_editor"],
                                           foreground="red",
                                           style="default.TLabel")
        self.label_song_editor.grid(padx = (0,50), column=1, row=1, sticky=(W))
        self.butt_seg = []
        for i in range(16):
            self.butt_seg.append(ttk.Button(self.frame_Song_editor,
                                            textvariable = self.butt_seg_txt_sv[i],
                                            command=partial(self.on_butt_seg, i),
                                            width=self.butt_seg_width,
                                            style="default.TButton"))

        for i in range(16):
            self.butt_seg[i].grid(ipady=self.ipady, column=i+2, row=1, sticky=(E))
        self.frame_Combo_song_patt = ttk.Frame(self.frame_Song_editor,
                                               style = "all.TFrame")
        self.frame_Combo_song_patt.grid(column=1, row=2, columnspan=17,  sticky=(W,S))
        self.label_song_expl = ttk.Label(self.frame_Combo_song_patt,
                                         text=self.widget_texts_dict["Song_expl"],
                                         foreground="black",
                                         style="default.TLabel")
        self.label_song_expl.grid(padx = (0,50), column=1, row=1, sticky=(W))
        self.song_patt_nr = []
        self.combo_song_patt = []
        self.combo_song_patt_repeat = []
        for i in range(4):
            self.song_patt_nr.append(ttk.Label(self.frame_Combo_song_patt,
                                     text=str(i+1),
                                     foreground="red",
                                     style="default.TLabel"))
            self.combo_song_patt.append(ttk.Combobox(self.frame_Combo_song_patt,
                                                     width=self.combo_drum_width,
                                                     textvariable=self.combo_song_patt_txt_sv[i],
                                                     font=self.standard_font,
                                                     style="default.TCombobox"))
            self.combo_song_patt_repeat.append(ttk.Combobox(self.frame_Combo_song_patt,
                                                            width=self.combo_repeat_width,
                                                            textvariable=self.combo_song_patt_repeat_txt_sv[i],
                                                            font=self.standard_font,
                                                            style="default.TCombobox"))
        for i in range(4):
            self.song_patt_nr[i].grid(padx = (0,5), pady = 10, ipady=self.ipady, column=i*3+2, row = 1, sticky=(S,W))
            self.combo_song_patt[i].grid(pady = 10, ipady=self.ipady, column=i*3+3, row = 1, sticky=(S,W))
            self.combo_song_patt[i]['values'] = self.drum_patterns_names
            self.combo_song_patt[i].current()
            self.combo_song_patt_repeat[i].grid(pady = 10,padx = (0,20), ipady=self.ipady, column=i*3+4, row = 1, sticky=(S,W))
            self.combo_song_patt_repeat[i]['values'] = [str(i) for i in range(1, 9)]
            self.combo_song_patt_repeat[i].current()
            if i == 0:
                self.combo_song_patt[i].bind("<<ComboboxSelected>>", self.combo_song_patt_1_bind)
                self.combo_song_patt_repeat[i].bind("<<ComboboxSelected>>", self.combo_song_patt_1_repeat_bind)
            elif i == 1:
                self.combo_song_patt[i].bind("<<ComboboxSelected>>", self.combo_song_patt_2_bind)
                self.combo_song_patt_repeat[i].bind("<<ComboboxSelected>>", self.combo_song_patt_2_repeat_bind)
            elif i == 2:
                self.combo_song_patt[i].bind("<<ComboboxSelected>>", self.combo_song_patt_3_bind)
                self.combo_song_patt_repeat[i].bind("<<ComboboxSelected>>", self.combo_song_patt_3_repeat_bind)
            elif i == 3:
                self.combo_song_patt[i].bind("<<ComboboxSelected>>", self.combo_song_patt_4_bind)
                self.combo_song_patt_repeat[i].bind("<<ComboboxSelected>>", self.combo_song_patt_4_repeat_bind)

        # Frame Play Save_song  +++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Song_play_save = ttk.Frame(self.frame_Main,
                                    borderwidth=3,
                                    relief='groove',
                                    padding="5 5 10 10",
                                    style = "all.TFrame")
        self.frame_Song_play_save.grid(column=1, row=6, columnspan=5,  sticky=(W,E))
        for column in range(1,19): # 17 columns
            self.frame_Song_play_save.columnconfigure(column, weight=1)
        for row in range(1,4):     # 3 rows
            self.frame_Song_play_save.rowconfigure(row, weight=1)

        self.frame_Song_play = ttk.Frame(self.frame_Song_play_save, style="all.TFrame")
        self.frame_Song_play.grid(column=1, row=1, sticky=(W,N))
        self.butt_play_song = ttk.Button(self.frame_Song_play,
                                         text=self.widget_texts_dict["Play_song"],
                                         command=self.on_butt_play_song,
                                         width=self.button_width_small,
                                         style="important.TButton")
        self.butt_play_song.grid(ipady=self.ipady, column=1, row=1, sticky=(W))
        self.butt_stop_play_song = ttk.Button(self.frame_Song_play,
                                              text=self.widget_texts_dict["Stop_playing_song"],
                                              command=self.on_butt_stop_playing_song,
                                              width=self.button_width_small,
                                              style="pressed.TButton")
        self.butt_stop_play_song.grid(ipady=self.ipady, column=2, row=1, sticky=(W))





        self.frame_Song_save = ttk.Frame(self.frame_Song_play_save, style="all.TFrame")
        self.frame_Song_save.grid(column=2, row=1, sticky=(W,N))
        self.butt_get_song = ttk.Button(self.frame_Song_save,
                                        text=self.widget_texts_dict["Open_song"],
                                        command=self.on_butt_open_song_file,
                                        width=self.button_width,
                                        style="default.TButton")
        self.butt_get_song.grid(ipady=self.ipady, column=1,row=1,sticky=(W))
        self.butt_save_midifile = ttk.Button(self.frame_Song_save,
                                             text=self.widget_texts_dict["Save_midifile"],
                                             command=self.on_butt_save_midifile,
                                             width=self.button_width,
                                             style="default.TButton")
        self.butt_save_midifile.grid(ipady=self.ipady, column=2,row=1,sticky=(W))

        # frame Textbox +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Textbox = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_Textbox.grid(column=1, row=7, columnspan=2,  sticky=(W,E))
        for column in range(1,3): # 2 columns
            self.frame_Textbox.columnconfigure(column, weight=10)
        for row in range(1,3):    # 2 rows
            self.frame_Textbox.rowconfigure(row, weight=10)
        self.txt_win = Text(self.frame_Textbox,
                            font=self.textbox_font,
                            state='normal',
                            width = self.text_win_width,
                            height = self.text_win_height)
        self.txt_win.grid(column=1, row=1, sticky=(N,S,E))
        self.textwindow_insert(self.welcome_txt + "\n\n")
        self.scrollbar = ttk.Scrollbar(self.frame_Textbox,
                                       orient=VERTICAL,
                                       command=self.txt_win.yview)
        self.scrollbar.grid(column=2, row=1, sticky=(N,S,W))
        self.txt_win.configure(yscrollcommand=self.scrollbar.set)

        # frame Footer: Quit ++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Footer = ttk.Frame(self.frame_Main,
                                      borderwidth=3,
                                      padding="5 5 10 10",
                                      relief='groove',
                                      style="all.TFrame")
        self.frame_Footer.grid(column=1, row=8, columnspan=2,  sticky=(S,W,E))
        for column in range(1,3): # 2 columns
            self.frame_Footer.columnconfigure(column, weight=1)
        for row in range(1,2):    # 1 rows
            self.frame_Footer.rowconfigure(row, weight=1)
        self.butt_clear_win = ttk.Button(self.frame_Footer,
                                         text=self.widget_texts_dict["Clear Textwindow"],
                                         command=self.clear_textwindow,
                                         width=self.button_width,
                                         style="default.TButton")
        self.butt_clear_win.grid(ipady=self.ipady, column=1, row=1, sticky=(W,S))
        #self.butt_reset_png = ttk.Button(self.frame_Footer,
        #                                 text=self.widget_texts_dict["Clear PNG"],
        #                                 command=self.on_butt_reset_png,
        #                                 width=self.button_width_normal,
        #                                 style="default.TButton")
        #self.butt_reset_png.grid(ipady=self.ipady, column=2, row=1, sticky=(W,S))
        self.butt_quit = ttk.Button(self.frame_Footer,
                                    text=self.widget_texts_dict["Quit"],
                                    command=self.on_close,
                                    width=self.button_width,
                                    style="default.TButton")
        self.butt_quit.grid(ipady=self.ipady, column=3, row=1,sticky=(S,E))




        self.UpdateTime()

        # Padding
        for child in self.frame_Main.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Fontsize.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Connect.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        #for child in self.frame_PNG.winfo_children():
        #    child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Textbox.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Footer.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)

                # Don't show the song editor at start
        self.frame_Song_editor.grid_remove()
        self.frame_Song_play_save.grid_remove()


        self.mainWin.mainloop()

def start_gui(flags_2_main, queue_2_main, queue_2_gui):
    gui = GUI(flags_2_main, queue_2_main, queue_2_gui)
    gui.run()
