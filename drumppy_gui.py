from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from time import strftime, localtime, sleep
import queue
from functools import partial # to pass argument from profile buttons
import json
from drumppy_instruments import instruments
import importlib

class GUI:
    def __init__(self, flags_2_main, queue_2_main, queue_2_gui):
        self.music_genres = ["pop_rock","reggae","rock","pop"]
        self.standard_font = ["Helvetica", 12, "bold"]
        self.standard_font_big = ["Helvetica", 20, "bold"]
        self.standard_font_small = ["Helvetica", 8, "bold"]
        self.textbox_font = ["Courier", 12, "bold"]
        self.welcome_txt = "Hello to DRUMPPY V0.2 alpha (2025)"
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
        self.channels_nrs = [str(i) for i in range(1, 17)]  # MIDI channels 1-16
        self.drum_patterns = []
        self.drum_patterns_names = []
        self.drum_patterns_module_filename = ""
        self.chosen_instrument_drum_names = []
        self.chosen_midi_port = ""
        self.chosen_instrument_name = ""
        self.chosen_channel = 1
        self.chosen_pattern_name = ""
        self.chosen_pattern_index = 0
        self.lock = ""
        self.velocity_1 = 0
        self.velocity_2 = 64
        self.velocity_3 = 120
        self.bpm_1 = 60
        self.bpm_2 = 120
        self.bpm_3 = 180
         # Dictionary for widget texts (inside:message)
        self.widget_texts_dict = {"Title" : "DRUMPPY V0.2 (2025)",
                                  "Midi_ports" : "MIDI ports",
                                  "Connect" : "Connect",
                                  "Connected" : "Connected",
                                  "Rescan" : "Rescan MIDI ports",
                                  "Chosen_port" : "Chosen MIDI port:",
                                  "Playing" : "Connected, playing some notes",
                                  "Instruments" : "Instrument",
                                  "Choose_instrument" : "Choose instrument",
                                  "Rescan_instruments" : "Rescan instruments",
                                  "Channels" : "Channel",
                                  "Patterns" : "Pattern",
                                  "Genre" : "Music genre",
                                  "Save" : "Save",
                                  "Save_as" : "Save as",
                                  "Pattern_editor": "Pattern editor",
                                  "Velocity" : "MIDI velocity: ",
                                  "Free" : "Free",
                                  "Locked" : "Lock",
                                  "Play_pattern" : "PLAY",
                                  "Stop_playing_pattern" : "STOP",

                                  "Clear PNG": "Reset Chart",
                                  "Clear Textwindow" : "Clear Textwindow",
                                  "Quit" : "Quit"
                                 }
        self.widget_texts_list = list(self.widget_texts_dict.keys())
        self.padx = 5
        self.pady = 5
        self.ipady = 6
        self.button_width_big = 38
        self.button_width = 27
        self.button_width_small = 16
        self.butt_patt_width = 5
        self.butt_mute_width = 6
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
            if len(message) == 1:
                self.textwindow_insert(message)
            else:
                self.textwindow_insert(f"{message}\n")
            self.txt_win.see("end")
            message = message.split('\n')
            if message[0] == "Error:":
                self.textwindow_insert(f"{message}\n")
                self.txt_win.see("end")
            elif message[0] == "Midi_ports:":
                self.midi_port_names = message[1:]
                print(self.midi_port_names)
                try:
                    self.combo_midi_port['values'] = self.midi_port_names
                    self.combo_midi_port.current(1)
                except:
                    pass
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
            self.instrument.set(self.instruments_names[index])
            self.chosen_channel = self.instruments_channels[index]
            self.channel.set(self.chosen_channel)
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
        """ Get drum_patterns and their names and send it to main """
        try:
            self.drum_patterns_module_filename = f"drumppy_patterns_{music_genre}.py"
            drum_patterns_module_name = f"drumppy_patterns_{music_genre}"
            drum_patterns_module = importlib.import_module(drum_patterns_module_name)
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
        text = f"Patterns:\n{drum_patterns_module_name}\n{json.dumps(self.drum_patterns_names)}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main

    def load_drum_pattern(self):
        """"""
        # Clean pattern
        for i in range(8):
            self.butt_mute[i].configure(style="mute_butt.TButton")
            self.butt_mute_txt[i].set("Mute")
            self.combo_drum_txt[i].set("")
            for j in range(16):
                self.butt_patt[j+i*16].configure(style="patt_butt_off.TButton")
                self.butt_patt_txt[j+i*16].set("")
        self.chosen_instrument_name = self.instrument.get()
        self.chosen_pattern_name = self.pattern.get()
        self.textwindow_insert(f"Chosen Pattern: {self.chosen_pattern_name}\n")
        try:
            for i in range(len(self.drum_patterns)):
                if self.chosen_pattern_name == self.drum_patterns[i][0]["pattern_name"]:
                    self.chosen_pattern_index = i
        except:
            text = "error: pattern not found"
            print(text)
            self.textwindow_insert(text + "\n")
            return
        # get pattern midi channel and send it to main
        self.chosen_channel = self.drum_patterns[self.chosen_pattern_index][0]["midi_channel"]
        self.channel.set(self.chosen_channel)
        text = f"Chosen_pattern:\n{self.chosen_instrument_name}\n{self.chosen_pattern_name}\n{self.bpm.get()}\n{self.chosen_channel}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main
        nr_of_drums = self.drum_patterns[self.chosen_pattern_index][0]["nr_of_drums"]
        for i in range(nr_of_drums):
            self.combo_drum_txt[i].set(self.drum_patterns[self.chosen_pattern_index][i+1]["drum_name"])
            if self.drum_patterns[self.chosen_pattern_index][i+1]["muted"] == "y":
                self.butt_mute[i].configure(style="muted_butt.TButton")
                self.butt_mute_txt[i].set("Muted")
            for j in range(16):

                str_vel = str(self.drum_patterns[self.chosen_pattern_index][i+1][j+1][1])
                if self.drum_patterns[self.chosen_pattern_index][i+1][j+1][0] == 1: # both beginning with 1
                    self.butt_patt[j+i*16].configure(style="patt_butt_on.TButton")
                    self.butt_patt_txt[j+i*16].set(str_vel)
                else:
                    self.butt_patt[j+i*16].configure(style="patt_butt_off.TButton")
                    self.butt_patt_txt[j+i*16].set(str_vel)
        # check lock
        self.lock = self.drum_patterns[self.chosen_pattern_index][0]["locked"]
        if self.lock == "n":
            self.butt_lock.configure(text = self.widget_texts_dict["Free"], style="pressed.TButton")
        else:
            self.butt_lock.configure(text = self.widget_texts_dict["Locked"], style="important.TButton")
        self.textwindow_insert(f"Pattern chosen: {self.chosen_pattern_name}\n")

    ###### Functions for Connect frame: Connect to MIDI port #####
    def on_butt_connect(self):
        """ Command connect button (MIDI ports) """
        self.chosen_midi_port = self.midi_port.get()
        self.retrieve_instr_data(self.chosen_midi_port)
        self.midi_port_label.set(self.chosen_midi_port)
        self.textwindow_insert(f"Chosen MIDI Port: {self.chosen_midi_port}\n")
        text = f"Midi_port:\n{self.chosen_midi_port}\n{self.chosen_channel}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main
        self.textwindow_insert(f"{self.widget_texts_dict['Playing']}\n")
        self.butt_connect.configure(style="pressed.TButton",
                                    text=self.widget_texts_dict['Connected'])
        self.load_drum_pattern()

    def combo_midi_port_bind(self, event):
        """ Binding to combobox MIDI ports """
        self.chosen_midi_port = self.midi_port.get()
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
        self.chosen_instrument_name = self.instrument.get()
        self.textwindow_insert(f"Instrument changed to: {self.chosen_instrument_name}\n")
        text = f"Instrument change:\n{self.chosen_instrument_name}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def combo_channel_bind(self, event):
        """ Binding to combobox channel """
        self.chosen_channel = self.channel.get()
        self.textwindow_insert(f"Channel changed to: {self.chosen_channel}\n")
        text = f"Channel change:\n{self.chosen_channel}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    ###### Functions for Connect frame: Chose genre and pattern ######
    def combo_genre_bind(self, event):
        chosen_genre = self.music_genre.get()
        self.get_drum_patterns(chosen_genre)

        self.combo_patt['values'] = self.drum_patterns_names
        self.combo_patt.current(0)
        self.textwindow_insert(f"Genre changed to: {chosen_genre}\n")
        text = f"Genre change:\n{chosen_genre}\n{self.drum_patterns_names}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def combo_patt_bind(self, event):
        """"""
        self.load_drum_pattern()

    ###### Functions for Connect frame: Save and Save as ######
    def on_butt_save(self):
        if self.lock == "y":
             text = 'This pattern is locked !! Choose "Save as" with a new name or unlock.\n'
             self.textwindow_insert(text)
             return
        else:
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
            with open(self.drum_patterns_module_filename, "w") as f:
            #with open("t.py", "w") as f:
                f.write(mtext)
            text = 'Pattern is saved!\n'
            self.textwindow_insert(text)




    def on_butt_save_as(self):
        pass

    ###### Functions pattern editor frame (drum, pad, mute, velocity) ######
    # I didn't find a fast way to pass a variable with the bindings
    def combo_drum_1_bind(self, event):
        """ Binding to combobox drum nr 1 """
        drum_name = self.combo_drum_txt[0].get()
        self.drum_patterns[self.chosen_pattern_index][1]["drum_name"] = drum_name

    def combo_drum_2_bind(self, event):
        """ Binding to combobox drum nr 2 """
        drum_name = self.combo_drum_txt[1].get()
        self.drum_patterns[self.chosen_pattern_index][2]["drum_name"] = drum_name

    def combo_drum_3_bind(self, event):
        """ Binding to combobox drum nr 3 """
        drum_name = self.combo_drum_txt[2].get()
        self.drum_patterns[self.chosen_pattern_index][3]["drum_name"] = drum_name

    def combo_drum_4_bind(self, event):
        """ Binding to combobox drum nr 4 """
        drum_name = self.combo_drum_txt[3].get()
        self.drum_patterns[self.chosen_pattern_index][4]["drum_name"] = drum_name

    def combo_drum_5_bind(self, event):
        """ Binding to combobox drum nr 5 """
        drum_name = self.combo_drum_txt[4].get()
        self.drum_patterns[self.chosen_pattern_index][5]["drum_name"] = drum_name

    def combo_drum_6_bind(self, event):
        """ Binding to combobox drum nr 6 """
        drum_name = self.combo_drum_txt[5].get()
        self.drum_patterns[self.chosen_pattern_index][6]["drum_name"] = drum_name

    def combo_drum_7_bind(self, event):
        """ Binding to combobox drum nr 7 """
        drum_name = self.combo_drum_txt[6].get()
        self.drum_patterns[self.chosen_pattern_index][7]["drum_name"] = drum_name

    def combo_drum_8_bind(self, event):
        """ Binding to combobox drum nr 8 """
        drum_name = self.combo_drum_txt[7].get()
        self.drum_patterns[self.chosen_pattern_index][8]["drum_name"] = drum_name

    def on_butt_pad(self,nr):
        """ One of 128 pads is pressed"""
        drum_nr = (nr//16)+1
        tick_nr = (nr%16)+1
        if self.butt_patt_txt[nr].get() == '':
            butt_patt_vel = 0
        else:
            butt_patt_vel = int(self.butt_patt_txt[nr].get())
        vel_s = self.velocity.get() # string
        vel = int(self.velocity.get())
        if butt_patt_vel == 0:
             self.drum_patterns[self.chosen_pattern_index][drum_nr][tick_nr] = [1,64]
             self.butt_patt[nr].configure(style="patt_butt_on.TButton")
             self.butt_patt_txt[nr].set(vel_s)
        else:
             self.drum_patterns[self.chosen_pattern_index][drum_nr][tick_nr] = [0,0]
             self.butt_patt[nr].configure(style="patt_butt_off.TButton")
             self.butt_patt_txt[nr].set(0)

    def on_butt_mute(self,nr):
        drum_nr = nr+1
        if self.butt_mute_txt[nr].get() == "Mute":
            self.drum_patterns[self.chosen_pattern_index][drum_nr]["muted"] = "y"
            self.butt_mute[nr].configure(style="muted_butt.TButton")
            self.butt_mute_txt[nr].set("Muted")
        else:
            self.drum_patterns[self.chosen_pattern_index][drum_nr]["muted"] = "n"
            self.butt_mute[nr].configure(style="mute_butt.TButton")
            self.butt_mute_txt[nr].set("Mute")

    def scale_velocity_bind(self, event):

        print(event)
        vel = self.velocity.get()
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] + str(vel))
        self.textwindow_insert(f"Velocity change: {vel}\n")

    def velocity_set_1(self):
        """ Set the Velocity to value 1 by pressing a button """
        self.velocity.set(self.velocity_1)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_1))
        self.textwindow_insert(f"Velocity change: {self.velocity_1}\n")

    def velocity_set_2(self):
        """ Set the Velocity to value 2 by pressing a button """
        self.velocity.set(self.velocity_2)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_2))
        self.textwindow_insert(f"Velocity change: {self.velocity_2}\n")

    def velocity_set_3(self):
        """ Set the Velocity to value 3 by pressing a button """
        self.velocity.set(self.velocity_3)
        self.label_velocity.config(text=self.widget_texts_dict["Velocity"] +
                                   str(self.velocity_3))
        self.textwindow_insert(f"Velocity change: {self.velocity_3}\n")

    def on_butt_lock(self):
        """ Toggle lock """
        if self.lock == "n":
            self.lock = "y"
            self.butt_lock.configure(text = self.widget_texts_dict["Locked"], style="important.TButton")
        else:
            self.lock = "n"
            self.butt_lock.configure(text = self.widget_texts_dict["Free"], style="pressed.TButton")
        self.drum_patterns[self.chosen_pattern_index][0]["locked"] = self.lock
        self.textwindow_insert(f"Lock changed to: {self.lock}\n")

    ###### Functions play frame (BPM, play, stop) ######
    def scale_bpm_bind(self, event):
        """ this is called when bpm scale changes"""
        bpm = self.bpm.get()
        self.label_bpm.config(text=f"BPM: {bpm}")
        self.textwindow_insert(f"BPM change: {bpm}\n")
        text = f"BPM change:\n{bpm}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def bpm_set_1(self):
        """ Set the BPM to a value 1 by pressing a button """
        self.bpm.set(self.bpm_1)
        self.label_bpm.config(text=f"BPM: {self.bpm_1}")
        self.textwindow_insert(f"BPM change: {self.bpm_1}\n")
        self.txt_win.see(self.end)
        text = f"BPM change:\n{self.bpm_1}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def bpm_set_2(self):
        """ Set the BPM to a value 2 by pressing a button """
        self.bpm.set(self.bpm_2)
        self.label_bpm.config(text=f"BPM: {self.bpm_2}")
        self.textwindow_insert(f"BPM change: {self.bpm_2}\n")
        text = f"BPM change:\n{self.bpm_2}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

    def bpm_set_3(self):
        """ Set the BPM to a value 3 by pressing a button """
        self.bpm.set(self.bpm_3)
        self.label_bpm.config(text=f"BPM: {self.bpm_3}")
        self.textwindow_insert(f"BPM change: {self.bpm_3}\n")
        text = f"BPM change:\n{self.bpm_3}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main

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
                         borderwidth=5)
        self.s.configure("pressed.TButton",          # New style for pressed button
                         background="lawngreen",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("patt_butt_on.TButton",          # New style for pressed button
                         background="firebrick1",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw")
        self.s.configure("patt_butt_off.TButton",          # New style for pressed button
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5,
                         justify="left",
                         anchor="nw")
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
        FSize = self.FSize.get()
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
        self.init_ttk_styles()
        self.get_drum_patterns(self.music_genres[0])
        self.get_instruments_names(instruments)
        self.FSize = StringVar()
        self.FSize.set("12")
        self.midi_port = StringVar()
        self.midi_port.set("")
        self.midi_port_label = StringVar()
        self.midi_port_label.set("")
        self.instrument = StringVar()
        self.instrument.set(self.instruments_names[0])
        self.music_genre = StringVar()
        self.music_genre.set(self.music_genres[0])
        self.pattern = StringVar()
        self.pattern.set(self.drum_patterns_names[0])
        self.channel = StringVar()
        self.channel.set(self.channels_nrs[0])
        self.butt_patt_txt = []
        for i in range(128):
            var = StringVar()
            var.set("")
            self.butt_patt_txt.append(var)
        self.combo_drum_txt = []
        for i in range(8):
            var = StringVar()
            var.set("")
            self.combo_drum_txt.append(var)
        self.butt_mute_txt = []
        for i in range(8):
            var = StringVar()
            var.set("Mute")
            self.butt_mute_txt.append(var)
        self.velocity = IntVar()
        self.velocity.set(64)
        self.bpm = IntVar()
        self.bpm.set(120)
        self.mainWin.protocol("WM_DELETE_WINDOW", self.on_close)
        self.mainWin.after(100, self.check_queue_from_main)  # Periodically check GUI queue
        self.mainWin.title(self.widget_texts_dict["Title"])
        self.mainWin.columnconfigure(0, weight=1)
        self.mainWin.rowconfigure(0, weight=1)
        # frame Main +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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

        # frame Header: Image with time and fontsize spinbox +++++++++++++++++++
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
        self.imageL1 = PhotoImage(file='drumppy.png')
        self.label_png = ttk.Label(self.frame_Header, text="",
                                   image=self.imageL1,
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
                                          textvariable=self.FSize,
                                          command=self.FontSizeUpdate, width=4,
                                          justify='center',
                                          font=self.standard_font,
                                          style="default.TSpinbox")
        self.spinb_fontsize.grid(column=2, row=1, sticky=(E))

        # frame Connect ++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        # Frame Midi port: 2 Buttons Connect, Rescan and Combobox ++++++++++++
        self.frame_Midi_port = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Midi_port.grid(column=1, row=1, sticky=(W))
        for row in range(1,4):
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
                                              textvariable=self.midi_port,
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
                                             textvariable=self.midi_port_label,
                                             style="default.TLabel")
        self.label_chosen_port_2.grid(pady = (5,0), column=1, row=5, sticky=(N,W,E))

        # Frame Instruments, Channels: 4 Label 2 Combobox ++++++++++++
        self.frame_Instruments = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Instruments.grid(column=2, row=1, sticky=(W))
        for row in range(1,6):
            self.frame_Instruments.rowconfigure(row, weight=1)
        self.butt_rescan = ttk.Button(self.frame_Instruments,
                                      text=self.widget_texts_dict["Rescan"],
                                      command=self.on_butt_rescan_midi_ports,
                                      width=self.button_width,
                                      style="default.TButton")
        self.butt_rescan.grid(pady=5, ipady=self.ipady, column=1,row=1, sticky=(W))

        self.label_instr = ttk.Label(self.frame_Instruments,
                                         text=self.widget_texts_dict["Instruments"],
                                         foreground="red",
                                         style="default.TLabel")
        self.label_instr.grid(pady = (5,0), column=1, row=2, sticky=(N,W,E))
        self.combo_instr = ttk.Combobox(self.frame_Instruments,
                                              width=self.button_width,
                                              textvariable=self.instrument,
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
                                             textvariable=self.channel,
                                             font=self.standard_font,
                                             style="default.TCombobox")
        self.combo_channel.grid(pady = 0, ipady=self.ipady, column=1, row=6, sticky=(S,W))
        self.combo_channel['values'] = self.channels_nrs
        self.combo_channel.current()
        self.combo_channel.bind("<<ComboboxSelected>>", self.combo_channel_bind)
        # Frame Patterns: 2 Buttons Connect, Rescan and Combobox ++++++++++++
        self.frame_Patterns = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Patterns.grid(column=3, row=1, sticky=(W))
        for row in range(1,6):
            self.frame_Patterns.rowconfigure(row, weight=1)
        self.label_genre = ttk.Label(self.frame_Patterns,
                                     text=self.widget_texts_dict["Genre"],
                                    foreground="red",
                                    style="default.TLabel")
        self.label_genre.grid(pady = (10,0), column=1, row=2, sticky=(N,W,E))
        self.combo_genre = ttk.Combobox(self.frame_Patterns,
                                       width=self.button_width,
                                       textvariable=self.music_genre,
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
                                       textvariable=self.pattern,
                                       font=self.standard_font,
                                       style="default.TCombobox")
        self.combo_patt.grid(pady = 5, ipady=self.ipady, column=1, row=5, sticky=(S,W))
        self.combo_patt['values'] = self.drum_patterns_names
        self.combo_patt.current(0)
        self.combo_patt.bind("<<ComboboxSelected>>", self.combo_patt_bind)
        # Frame Save
        self.frame_Save = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_Save.grid(column=4, row=1, sticky=(W))
        for row in range(1,6):
            self.frame_Patterns.rowconfigure(row, weight=1)
        self.butt_save = ttk.Button(self.frame_Save,
                                    text=self.widget_texts_dict["Save"],
                                    command=self.on_butt_save,
                                    width=self.button_width,
                                    style="default.TButton")
        self.butt_save.grid(ipady=self.ipady, column=1,row=1,sticky=(W))
        self.butt_save_as = ttk.Button(self.frame_Save,
                                    text=self.widget_texts_dict["Save_as"],
                                    command=self.on_butt_save_as,
                                    width=self.button_width,
                                    style="default.TButton")
        self.butt_save_as.grid(ipady=self.ipady, column=1,row=2,sticky=(W))


        # frame Pattern_editor  ++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        self.label_patt_editor.grid(pady = (20,0), column=1, row=1, sticky=(N,W,E))
        self.label_tick_nr = []
        for i in range(16):
            self.label_tick_nr.append(ttk.Label(self.frame_Patt_editor,
                                      text=str(i+1),
                                      foreground="red",
                                      #width = self.butt_patt_width,
                                      width = self.butt_patt_width,
                                      anchor="center",
                                      style="default.TLabel"))
            self.label_tick_nr[i].grid(pady = (20,0), column=i+3, row=1, sticky=(N,W,E))

        self.combo_drum = []
        for i in range(8):
            self.combo_drum.append(ttk.Combobox(self.frame_Patt_editor,
                                                width=self.combo_drum_width,
                                                textvariable=self.combo_drum_txt[i],
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
                                             textvariable = self.butt_mute_txt[i],
                                             command=partial(self.on_butt_mute, i),
                                             width=self.butt_mute_width,
                                             style="mute_butt.TButton"))

        for i in range(8):
            self.butt_mute[i].grid(pady = 10, padx = 10, ipady=self.ipady, column=2, row=i+2, sticky=(S,W))

        self.butt_patt = []
        for i in range(128):
            self.butt_patt.append(ttk.Button(self.frame_Patt_editor,
                                             textvariable=self.butt_patt_txt[i],
                                             command=partial(self.on_butt_pad, i),
                                             width=self.butt_patt_width,
                                             style="default.TButton"))
        for i in range(16):
            self.butt_patt[i].grid(ipady=self.ipady, column=i+3, row=2, sticky=(W,E))
            self.butt_patt[i+16].grid(ipady=self.ipady, column=i+3, row=3, sticky=(W,E))
            self.butt_patt[i+32].grid(ipady=self.ipady, column=i+3, row=4, sticky=(W,E))
            self.butt_patt[i+48].grid(ipady=self.ipady, column=i+3, row=5, sticky=(W,E))
            self.butt_patt[i+64].grid(ipady=self.ipady, column=i+3, row=6, sticky=(W,E))
            self.butt_patt[i+80].grid(ipady=self.ipady, column=i+3, row=7, sticky=(W,E))
            self.butt_patt[i+96].grid(ipady=self.ipady, column=i+3, row=8, sticky=(W,E))
            self.butt_patt[i+112].grid(ipady=self.ipady, column=i+3, row=9, sticky=(W,E))
        self.frame_velocity = ttk.Frame(self.frame_Patt_editor,
                                        style = "all.TFrame")
        self.frame_velocity.grid(column=1, row=10, columnspan=2,  sticky=(W,S))

        self.label_velocity = ttk.Label(self.frame_velocity,
                                           text=self.widget_texts_dict["Velocity"] + "64",
                                           foreground="red",
                                           style="default.TLabel")
        self.label_velocity.grid(pady = (20,0), column=1, row=1, sticky=(N,W,E))

        self.scale_velocity = ttk.Scale(self.frame_velocity,
                                   from_= 0,
                                   to=127,
                                   length=self.combo_drum_width*16,
                                   variable=self.velocity,
                                   style="default.Horizontal.TScale"
                                  )
        self.scale_velocity.grid(ipady=self.ipady, column=1, row=2, columnspan = 2, sticky=(W,S))
        self.scale_velocity.bind("<ButtonRelease-1>", self.scale_velocity_bind)

        self.butt_vel_1 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_1,
                                     command=self.velocity_set_1,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_vel_1.grid(ipady=self.ipady, column=3, row=10, sticky=(W,S))
        self.butt_vel_2 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_2,
                                     command=self.velocity_set_2,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_vel_2.grid(ipady=self.ipady, column=4, row=10, sticky=(W,S))
        self.butt_vel_3 = ttk.Button(self.frame_Patt_editor,
                                     text=self.velocity_3,
                                     command=self.velocity_set_3,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_vel_3.grid(ipady=self.ipady, column=5, row=10, sticky=(W,S))
        self.butt_lock = ttk.Button(self.frame_Patt_editor,
                                     text="",
                                     command=self.on_butt_lock,
                                     width=self.butt_patt_width,
                                     style="default.TButton")
        self.butt_lock.grid(ipady=self.ipady, column=18, row=10, sticky=(E))



        # frame Play  ++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Play = ttk.Frame(self.frame_Main,
                                    borderwidth=3,
                                    relief='groove',
                                    padding="5 5 10 10",
                                    style = "all.TFrame")
        self.frame_Play.grid(column=1, row=4, columnspan=5,  sticky=(W,E))
        for column in range(1,6): # 3 columns
            self.frame_Play.columnconfigure(column, weight=1)
        for row in range(1,3):    # 1 rows
            self.frame_Play.rowconfigure(row, weight=1)

        self.frame_Bpm = ttk.Frame(self.frame_Play,
                                   style = "all.TFrame")
        self.frame_Bpm.grid(pady = 0, column=1, row=1, sticky=(W))

        self.label_bpm = ttk.Label(self.frame_Bpm,
                                           text=f"BPM: 120",
                                           foreground="red",
                                           style="default.TLabel")
        self.label_bpm.grid(column=1, row=1, sticky=(N,W,E))

        self.scale_bpm = ttk.Scale(self.frame_Bpm,
                                   from_= 20,
                                   to=240,
                                   length=self.combo_drum_width*14,
                                   variable=self.bpm,
                                   style="default.Horizontal.TScale")
        self.scale_bpm.grid(padx = 0, ipady=self.ipady, column=1, row=2, sticky=(W,S))
        self.scale_bpm.bind("<ButtonRelease-1>", self.scale_bpm_bind)

        self.butt_bpm_1 = ttk.Button(self.frame_Bpm,
                                     text=self.bpm_1,
                                     command=self.bpm_set_1,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_bpm_1.grid(ipady=self.ipady, column=2, row=1, rowspan = 2, sticky=(W,S))
        self.butt_bpm_2 = ttk.Button(self.frame_Bpm,
                                     text=self.bpm_2,
                                     command=self.bpm_set_2,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_bpm_2.grid(ipady=self.ipady, column=3, row=1, rowspan = 2, sticky=(W,S))
        self.butt_bpm_3 = ttk.Button(self.frame_Bpm,
                                     text=self.bpm_3,
                                     command=self.bpm_set_3,
                                     width=self.butt_patt_width+1,
                                     style="velocity.TButton")
        self.butt_bpm_3.grid(ipady=self.ipady, column=4, row=1, rowspan = 2, sticky=(W,S))

        self.frame_Play_butt = ttk.Frame(self.frame_Play,
                                         style = "all.TFrame")
        self.frame_Play_butt.grid(pady = 0, column=2, row=1, sticky=(W))

        self.butt_play_patt = ttk.Button(self.frame_Play_butt,
                                         text=self.widget_texts_dict["Play_pattern"],
                                         command=self.on_butt_play_pattern,
                                         width=self.button_width_small,
                                         style="important.TButton")
        self.butt_play_patt.grid(ipady=self.ipady, column=1, row=1, sticky=(W))

        self.butt_stop_play_patt = ttk.Button(self.frame_Play_butt,
                                              text=self.widget_texts_dict["Stop_playing_pattern"],
                                              command=self.on_butt_stop_playing_pattern,
                                              width=self.button_width_small,
                                              style="pressed.TButton")
        self.butt_stop_play_patt.grid(ipady=self.ipady, column=2, row=1, sticky=(W))

        # frame Textbox +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Textbox = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_Textbox.grid(column=1, row=5, columnspan=2,  sticky=(W,E))
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
        self.frame_Footer.grid(column=1, row=6, columnspan=2,  sticky=(S,W,E))
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

        self.mainWin.mainloop()

def start_gui(flags_2_main, queue_2_main, queue_2_gui):
    gui = GUI(flags_2_main, queue_2_main, queue_2_gui)
    gui.run()
