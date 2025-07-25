import time
import sys
from mido import MidiFile, MidiTrack, Message, MetaMessage, tempo2bpm, get_output_names, open_output
from importlib import import_module # stl dynamically import module (name known during runtime)

class DrumppyMidiFile:
    def __init__(self): #, flags_2_main, queue_2_main, queue_2_gui):
        """ Initialize the DP100Functions class with queues for communication. """
        #self.queue_2_main = queue_2_main
        #self.queue_2_gui = queue_2_gui
        #self.flags_2_main = flags_2_main
        self.midi_ports = []
        self.midi_port = ""
        self.ppqn = 480
        self.dt_1_16 = int(self.ppqn/4) # with ppqn = 480 we get 120

    def check_port(self, midi_port = "CH345:CH345 MIDI 1"):  # "USB MIDI 2x2:USB MIDI 2x2 MIDI 1"
        """Function to check if a specific MIDI port is available."""
        try:
            for port in get_output_names():
                if midi_port in port:
                    return port
            return "None"
        except Exception as e:
            print(f"Error retrieving MIDI output port: {e}")

    def create_simple_midi_file(self, filename):
        mfile = MidiFile(type=1) # Type = 1
        mfile.ticks_per_beat = self.ppqn # Set the number of ticks per quarter note
        mtrack0 = MidiTrack() # first track with infos
        mtrack1 = MidiTrack() # second track with notes
        mfile.tracks.append(mtrack0)
        mfile.tracks.append(mtrack1)
        bpm = 120 # 500000 microseconds per quarter at 120bpm
        tempo = int(tempo2bpm(bpm))
        ### first track ###
        mtrack0.append(MetaMessage('copyright', text='CC BY-SA'))
        mtrack0.append(MetaMessage('cue_marker', text='Created by weigu (DRUMMPY)'))
        mtrack0.append(MetaMessage('cue_marker', text='http://www.weigu.lu'))
        mtrack0.append(MetaMessage('set_tempo', tempo=tempo))
        mtrack0.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8))
        mtrack1.append(MetaMessage('end_of_track', time=0))
        ### second track ###
        mtrack1.append(MetaMessage('track_name', name='simple_drum_pattern'))
        for i in range(2):
            if i == 0:
                mtrack1.append(Message('note_on', channel=9, note=36, velocity=64, time=0))       # kick on
            else:
                mtrack1.append(Message('note_on', channel=9, note=36, velocity=64, time=self.dt_1_16)) # kick on
            mtrack1.append(Message('note_on', channel=9, note=42, velocity=64, time=0))           # hi-hat on
            mtrack1.append(Message('note_on', channel=9, note=42, velocity=64, time=0))           # hi-hat on
            mtrack1.append(Message('note_off', channel=9, note=36, velocity=64, time=self.dt_1_16))    # kick off
            mtrack1.append(Message('note_off', channel=9, note=42, velocity=64, time=0))          # hi-hat off
            mtrack1.append(Message('note_on', channel=9, note=42, velocity=64, time=self.dt_1_16))     # hi-hat on
            mtrack1.append(Message('note_off', channel=9, note=42, velocity=64, time=self.dt_1_16))    # hi-hat off
            mtrack1.append(Message('note_on', channel=9, note=38, velocity=64, time=self.dt_1_16))     # snare on
            mtrack1.append(Message('note_on', channel=9, note=42, velocity=64, time=0))           # hi-hat on
            mtrack1.append(Message('note_off', channel=9, note=38, velocity=64, time=self.dt_1_16))    # snare off
            mtrack1.append(Message('note_off', channel=9, note=42, velocity=64, time=0))          # hi-hat off
            mtrack1.append(Message('note_on', channel=9, note=42, velocity=64, time=self.dt_1_16))     # hi-hat on
            mtrack1.append(Message('note_off', channel=9, note=42, velocity=64, time=self.dt_1_16))    # hi-hat off
        mtrack1.append(MetaMessage('end_of_track', time=self.dt_1_16)) # length overall = 16/16 notes
        mfile.save(filename)

    def get_pattern(self, music_genre, pattern_name):
        patterns_module_name = f"drumppy_patterns.drumppy_patterns_{music_genre}"
        drum_patterns_module = import_module(patterns_module_name)
        drum_patterns = drum_patterns_module.drum_patterns
        for i in range(len(drum_patterns)):
            if drum_patterns[i][0]["pattern_name"] == pattern_name:
                return drum_patterns[i]

    def get_instrument(self, instr_name):
        instr_module = import_module("drumppy_instruments")
        instr = instr_module.instruments
        for i in range(len(instr)):
            if instr[i]["instrument_name"] == instr_name:
                return instr[i]

    def create_event_list(self, instrument, pattern, steps_2_play, nr_of_drums, first_dt):
        events = [] #event array: time absolute, command, note, vel
        for j in range(1, int(steps_2_play) + 1): # steps to play
            for i in range(1,nr_of_drums + 1):
                if pattern[i]["drum_name"] != "" and pattern[i]["muted"] == "n":
                    if pattern[i][j][0]: # note_on
                        if len(pattern[i][j]) > 2: # we get different stretch and/or a delay
                            delay = pattern[i][j][2] # delay unit is 1/256 note (0-15 for 1/16 note)
                            tick_delay = int(delay*7.5)
                        else:
                            tick_delay = 0
                        if pattern[i][j][0] & 0b0000_1110 != 0:
                            roll = (pattern[i][j][0] & 0b0001_1110) >> 1
                            dt = int(self.dt_1_16/roll)
                            for k in range(0,roll):
                                events.append([(((j-1)*self.dt_1_16)+(k*dt)+tick_delay),"note_on",instrument[pattern[i]["drum_name"]],pattern[i][j][1]])
                                events.append([(((j-1)*self.dt_1_16)+((k+1)*dt)+tick_delay),"note_off",instrument[pattern[i]["drum_name"]],pattern[i][j][1]])
                        else:
                            events.append([(j-1)*self.dt_1_16+tick_delay,"note_on",instrument[pattern[i]["drum_name"]],pattern[i][j][1]])
                            events.append([(j)*self.dt_1_16+tick_delay,"note_off",instrument[pattern[i]["drum_name"]],pattern[i][j][1]])
        events.sort(key=lambda x: x[0]) # Sort in-place
        return events

    def create_pattern_midi_file(self, instrument, pattern, filename, first_dt= 0):
        """     dt stands for delta time in ticks """
        print(pattern)
        mfile = MidiFile(type=1) # Type = 1
        mfile.ticks_per_beat = self.ppqn # Set the number of ticks per quarter note
        mtrack0 = MidiTrack() # first track with infos
        mtrack1 = MidiTrack() # second track with notes
        mfile.tracks.append(mtrack0)
        mfile.tracks.append(mtrack1)
        bpm = pattern[0]["bpm"]
        pattern_name = pattern[0]["pattern_name"]
        ch = pattern[0]["midi_channel"]-1 # MIDO 0-15
        steps_2_play = pattern[0]["steps_2_play"]
        nr_of_drums = pattern[0]["nr_of_drums"]
        tempo = int(tempo2bpm(bpm))
        tick_end = steps_2_play*self.dt_1_16
        tick_delay = 0
        events = self.create_event_list(instrument, pattern, steps_2_play, nr_of_drums, first_dt)
        ### first track ###
        mtrack0.append(MetaMessage('copyright', text='CC BY-SA'))
        mtrack0.append(MetaMessage('cue_marker', text='Created by weigu (DRUMMPY)'))
        mtrack0.append(MetaMessage('cue_marker', text='http://www.weigu.lu'))
        mtrack0.append(MetaMessage('set_tempo', tempo=tempo))
        mtrack0.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8))
        mtrack1.append(MetaMessage('end_of_track', time=0))
        ### second track ###
        mtrack1.append(MetaMessage('track_name', name=pattern_name))
        for i in range(len(events)):
            #print(i)
            if events[i][0] == 0:
                mtrack1.append(Message(events[i][1], channel=ch, note=events[i][2], velocity=events[i][3], time=0))
            else:
                dt = events[i][0] - events[i-1][0]
                mtrack1.append(Message(events[i][1], channel=ch, note=events[i][2], velocity=events[i][3], time=dt))

        if tick_end != events[-1][0]:
            mtrack1.append(MetaMessage('end_of_track', time=tick_end-events[-1][0])) # length overall = 16/16 notes
        else:
            mtrack1.append(MetaMessage('end_of_track', time=0)) # length overall = 16/16 notes
        mfile.save(filename)


    def play_midi_file(self, mport, filename):
        mfile = MidiFile(filename)
        for msg in mfile: # get tempo
          if msg.type == 'set_tempo':
              tempo2 = msg.tempo
              print(tempo2)
        with open_output(mport) as outport:
          for message in mfile.play():
              t0 = time.time()
              print(message)
              outport.send(message)
              #time.sleep(mido.tick2second(msg.time, mid.ticks_per_beat, tempo2)) #Adjust tempo if needed


    def analyse_midi_file(self, filename):
        """ Open a MIDI file and print every message in every track."""
        mfile = MidiFile(filename)
        print(f"File format: {mfile.type}")
        print(f"Ticks per quarter note: {mfile.ticks_per_beat}")
        for i, track in enumerate(mfile.tracks):
            print(f'=== Track {i}')
            for message in track:
                print(f'  {message!r}')

### main ####
def main():
    """setup and start mainloop"""
    print ('Argument list: ', sys.argv)

    music_genre = "pop_rock"
    #pattern_name = "flashdance_maniac_cp_1"
    pattern_name = "basic_pop_beat_1"
    pattern_file = f"drumppy_pattens/drumppy_patterns_{music_genre}.py"

    if len(sys.argv) == 2:
        local_directory = sys.argv[1]

    filename_3 = "drum_pattern.mid"
    #port = "Pico:Pico CircuitPython usb_midi.por"
    instrument = "nano_synth"

    mf = DrumppyMidiFile()
    instrument = mf.get_instrument(instrument)
    port = instrument["midi_port"]

    pattern = mf.get_pattern(music_genre, pattern_name)
    filename = "test.mid"
    mf.create_pattern_midi_file(instrument, pattern, filename, 0)
    mf.play_midi_file(port, filename)

    #if mf.check_port(port)==port:
    #    print("Port is OK!")
    #mf.create_simple_midi_file(filename_2)
    mf.analyse_midi_file(filename)


if __name__ == '__main__':
    main()
