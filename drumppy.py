#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

""" Drum Pattern Python GUI program """
###############################################################################
#
#  drumppy.py
#
#  Version 1.0 2025-06
#
#  Copyright 2025 weigu <weigu@weigu.lu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
###############################################################################

import threading
import os
from time import gmtime, strftime, localtime, sleep
import queue
from drumppy_gui import start_gui, GUI
from drumppy_functions import DrumppyFunctions
import json

def main_loop(dp, flags_2_main, queue_2_main, queue_2_gui):
    """Main loop for handling device communication and GUI updates"""
    dp.create_music_genres_files()  # Create music genres files if they don't exist
    try:
        while not flags_2_main["flag_exit"].is_set():  # Check the exit flag
            if flags_2_main["flag_midi_port"].is_set():
                #dp.send_identity_request(chosen_midi_port)
                #dp.play_some_notes(chosen_midi_port)  # Test MIDI port
                flags_2_main["flag_midi_port"].clear()
            if flags_2_main["flag_rescan"].is_set():
                dp.get_midi_ports()
                flags_2_main["flag_rescan"].clear()
            if flags_2_main["flag_play_patt"].is_set():
                dp.play_drum_pattern()
            if flags_2_main["flag_stop_play_patt"].is_set():
                flags_2_main["flag_play_patt"].clear()
                flags_2_main["flag_stop_play_patt"].clear()
            if flags_2_main["flag_play_song"].is_set():
                dp.play_song()
                flags_2_main["flag_play_song"].clear()
            if flags_2_main["flag_stop_play_song"].is_set():
                flags_2_main["flag_play_patt"].clear()

                flags_2_main["flag_stop_play_song"].clear()
            try:
                message = queue_2_main.get_nowait()
                message = message.split('\n')
                print(f"Message from GUI: {message}")
                if message[0] == "Midi_port:":
                    dp.chosen_midi_port = message[1]
                    dp.chosen_channel = message[2]
                    flags_2_main["flag_midi_port"].set()
                if message[0] == "Patterns:":
                    dp.drum_patterns_module_name = message[1]
                    dp.drum_patterns_names = json.loads(message[2])
                    dp.load_drum_patterns()
                if message[0] == "Instruments_names:":
                    dp.instruments_names = json.loads(message[1])
                if message[0] == "Chosen_genre:":
                    dp.chosen_genre = message[1]
                    dp.get_drum_patterns(dp.music_genres[0])
                    dp.load_drum_patterns()
                if message[0] == "Chosen_pattern:":
                    dp.chosen_instrument = message[1]
                    dp.chosen_pattern = message[2]
                    dp.chosen_bpm = message[3]
                    dp.chosen_channel = message[4]
                    dp.ticks_2_play = message[5]
                if message[0] == "BPM change:":
                    dp.chosen_bpm = message[1]
                if message[0] == "Instrument change:":
                    dp.chosen_instrument = message[1]
                if message[0] == "Channel change:":
                    dp.chosen_channel = message[1]
                if message[0] == "Song_loaded:":
                    dp.chosen_song = json.loads(message[1])
                if message[0] == "Ticks_2_play_change:":
                   dp.ticks_2_play = message[1]


            except queue.Empty:
                pass
            sleep(0.01)  # Prevent busy-waiting
    except KeyboardInterrupt:
        print("Keyboard interrupt by user")
    print("Main loop terminated.")

def main():
    """Setup and start main loop"""
    print("Program started! Version 3.0 (2025)")
    flags_2_main = {"flag_midi_port": 0,
                    "flag_rescan" : 1,
                    "flag_play_patt" : 2,
                    "flag_stop_play_patt" : 3,
                    "flag_play_song" : 4,
                    "flag_stop_play_song" : 5,
                    "flag_exit" : 6}
    for f in flags_2_main:
        flags_2_main[f] = threading.Event()

    queue_2_main = queue.Queue()  # Queue for communication from GUI to main_loop
    queue_2_gui = queue.Queue()   # Queue for communication from main_loop to GUI
    queue_2_png = queue.Queue()   # Queue for communication from main_loop to PNG creation thread

    dp = DrumppyFunctions(flags_2_main, queue_2_main, queue_2_gui)

    # Create GUI, main loop, and PNG creation threads
    gui_thread = threading.Thread(target=start_gui, args=(flags_2_main, queue_2_main, queue_2_gui))
    main_thread = threading.Thread(target=main_loop, args=(dp, flags_2_main, queue_2_main, queue_2_gui))

    gui_thread.start()
    main_thread.start()

    try:
        gui_thread.join()  # Wait for GUI thread to finish
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    # Set the exit flag to stop the main loop and PNG thread
    flags_2_main["flag_exit"].set()
    # Wait for the main loop and PNG threads to finish
    main_thread.join()

    print("All threads terminated. Program exiting.")

if __name__ == '__main__':
    main()