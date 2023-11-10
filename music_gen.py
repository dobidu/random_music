from midiutil import MIDIFile
from music21 import *
from pydub import AudioSegment
from midi2audio import FluidSynth
from datetime import datetime
from pedalboard import Pedalboard, Compressor, Gain, Chorus, LadderFilter, Phaser, Delay, Reverb
from pedalboard.io import AudioFile
import time
import json
import random
import os
import glob
import musicality_score 

def generate_chord_progression(key, tempo, time_signature, measures, name, part, pattern_file):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Chord Progression")
    mf.addTempo(track, time, tempo)
    
    beats_per_measure = int(time_signature.split('/')[0])

    # Read chord patterns from a text file
    chord_patterns = {}
    with open(pattern_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                part_name, pattern = line.split(':')
                chord_patterns.setdefault(part_name, []).append(pattern.split(','))

    # Shuffle the list of chord patterns
    random.shuffle(chord_patterns.get(part, chord_patterns.get(part, [['I', 'IV', 'V', 'vi']])))
    # Choose a random chord pattern based on the part of the song
    chord_pattern = random.choice(chord_patterns.get(part, [['I', 'IV', 'V', 'vi']]))

    chord_progression = []
    for chord_symbol in chord_pattern:
        chord = roman.RomanNumeral(chord_symbol, key)
        chord_progression.append(chord)

    chord_duration = beats_per_measure / len(chord_pattern)
    for i in range(measures * len(chord_pattern)):
        chord = chord_progression[i % len(chord_progression)]
        for note in chord.pitches:
            mf.addNote(track, 0, note.midi, time, chord_duration, 100)
        time += chord_duration

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-chord_progression.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)

    print("\t\t\tChord pattern: " + str(chord_pattern))
    return chord_pattern, filename

def generate_melody(key, tempo, time_signature, measures, name, part, chord_progression):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Melody")
    mf.addTempo(track, time, tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Create scale based on key
    if key[-1] == 'm':
        scale_obj = scale.MinorScale(key[:-1])
    else:
        scale_obj = scale.MajorScale(key)

    # Create chord progression based on key and chord progression input
    chords = []
    for chord_symbol in chord_progression:
        chord_obj = roman.RomanNumeral(chord_symbol, key)
        chord_obj.key = key
        chords.append(chord_obj)

    # Determine which notes to use based on song part and chord progression
    if part == 'intro':
        notes_to_use = chords[0].pitches
    elif part == 'outro':
        notes_to_use = chords[-1].pitches
    else:
        notes_to_use = []
        for chord in chords:
            notes_to_use.extend(chord.pitches)

    # Define the Markov chain transition matrix
    # This matrix defines the probabilities of transitioning from one note to another
    transition_matrix = {}
    for note in notes_to_use:
        transition_matrix[note.midi] = {}
        for next_note in notes_to_use:
            if next_note in chord_obj.pitches:
                transition_matrix[note.midi][next_note.midi] = 1 / len(notes_to_use)
            else:
                transition_matrix[note.midi][next_note.midi] = 0

    # Generate a random melody using a Markov chain
    melody = []
    note_durations = []
    total_notes = measures * beats_per_measure

    # Choose the initial note randomly
    current_note = random.choice(list(transition_matrix.keys()))

    while total_notes > 0:
        # Choose the next note based on the Markov chain transition probabilities
        current_note = random.choices(
            population=list(transition_matrix[current_note].keys()),
            weights=list(transition_matrix[current_note].values())
        )[0]

        # Choose a random duration for the note
        note_duration = random.choice([1, 2])
        if note_duration > total_notes:
            note_duration = total_notes

        # Add the note to the melody
        melody.append(current_note)
        note_durations.append(note_duration)
        total_notes -= note_duration

    # Add notes to MIDI file
    for i in range(len(melody)):
        note = melody[i]
        note_duration = note_durations[i]
        velocity = random.randint(70, 100)
        mf.addNote(track, 0, note, time, note_duration, velocity)
        time += note_duration

    print("\t\t\tMelody: " + str(melody))

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-melody.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
    return melody, filename

def generate_bassline(key, tempo, time_signature, measures, name, part, chord_progression, melody):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Bassline")
    mf.addTempo(track, time, tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Create scale based on key
    if key[-1] == 'm':
        scale_obj = scale.MinorScale(key[:-1])
    else:
        scale_obj = scale.MajorScale(key)

    # Create chord progression based on key and chord progression input
    chords = []
    for chord_symbol in chord_progression:
        chord_obj = roman.RomanNumeral(chord_symbol, key)
        chord_obj.key = key
        chords.append(chord_obj)

    # Determine which notes to use based on song part and chord progression
    if part == 'intro':
        notes_to_use = [chords[0].pitches[0]]
    #    notes_to_use = [chords[0].root]
    elif part == 'outro':
        notes_to_use = [chords[-1].pitches[0]]
    #    notes_to_use = [chords[-1].root]
    else:
    #    notes_to_use = [chord.root for chord in chords]
        notes_to_use = [chord.pitches[0] for chord in chords]

    # Define the Markov chain transition matrix
    # This matrix defines the probabilities of transitioning from one note to another
    transition_matrix = {}
    for note in notes_to_use:
        transition_matrix[note.midi] = {}
        for next_note in notes_to_use:
            transition_matrix[note.midi][next_note.midi] = 1 / len(notes_to_use)

    # Generate a random bassline using a Markov chain
    bassline = []
    note_durations = []
    total_notes = measures * beats_per_measure

    # Choose the initial note randomly
    current_note = random.choice(list(transition_matrix.keys()))

    while total_notes > 0:
        # Choose the next note based on the Markov chain transition probabilities
        current_note = random.choices(
            population=list(transition_matrix[current_note].keys()),
            weights=list(transition_matrix[current_note].values())
        )[0]

        # Choose a random duration for the note
        note_duration = random.choice([1, 2])
        if note_duration > total_notes:
            note_duration = total_notes

        # Add the note to the bassline
        bassline.append(current_note)
        note_durations.append(note_duration)

        total_notes -= note_duration

    # Make sure the bassline follows the melody
    for i in range(len(bassline)):
        if i < len(melody):
            if bassline[i] != melody[i]:
                if random.random() < 0.5:
                    bassline[i] = melody[i]

    print("\t\t\tBassline: " + str(bassline))
    # Add notes to MIDI file
    for i in range(len(bassline)):
        note = bassline[i]
        note_duration = note_durations[i]
        velocity = random.randint(70, 100)
        
        # Set the octave of the note to 2 (bass range)
        note_obj = pitch.Pitch()
        note_obj.midi = note
        note_obj.octave = 2
        
        mf.addNote(track, 0, note_obj.midi, time, note_duration, velocity)
        time += note_duration

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-bassline.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
    return filename

def generate_beat(tempo,time_signature,measures,name,part,filename):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0 
    time = 0 
    mf.addTrackName(track,time,"Beat")
    mf.addTempo(track,time,tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Define drum sounds
    kick = 36 
    snare = 38 
    hihat = 42 

    # Read beat patterns from file
    beat_patterns = {}
    with open(filename,'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(':')
                song_part = parts[0].strip()
                beat_pattern = [int(x) for x in parts[1].split(',')]
                if song_part not in beat_patterns:
                    beat_patterns[song_part] = []
                beat_patterns[song_part].append(beat_pattern)
    # Create a beat
    beat = []

    # Choose a random beat pattern based on song part and available patterns from file
    if part in beat_patterns:
        beat_pattern = random.choice(beat_patterns[part])
    else:
        beat_pattern = [kick, 0, snare, 0]
    	
    # Repeat the pattern for the number of measures - 1    
    for i in range(measures-1):
        beat.extend(beat_pattern)

    # Choose a random beat roll pattern based on song part and available patterns from file
    roll_part = part + "_roll"
    
    if roll_part in beat_patterns:
        roll_pattern = random.choice(beat_patterns[roll_part])
    else:
        roll_pattern = [kick , snare, snare, snare]
    
    beat.extend(roll_pattern)
    
    # Add notes to MIDI file
    for i in range(len(beat)):
        drum_sound = beat[i]
        if drum_sound != 0:
            mf.addNote(track ,9 ,drum_sound ,time ,1.0/beats_per_measure ,100)
        time +=1.0/beats_per_measure

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-beat.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
    
    print("\t\t\tBeat: " + str(beat))
    return filename

def generate_song_parts(key, tempo, time_signature, song_measures, name, chord_pat_file, beat_pat_file):
    print("Generating song parts for: " + name)
    print("\tKey: " + key)
    print("\tTempo: " + str(tempo))
    print("\tTime signature: " + time_signature)
    harm_filename = {}
    bass_filename = {}
    melo_filename = {}
    beat_filename = {}
    for part, measures in song_measures.items():
        print("\t\tGenerating part: " + part + " (" + str(measures) + " measures)")
        name_part = name + "-" + part
        chord_progression, harm_filename[part] = generate_chord_progression(key, tempo, time_signature, measures, name_part, part, chord_pat_file)
        melody, melo_filename[part] = generate_melody(key, tempo, time_signature, measures, name_part, part, chord_progression)
        bass_filename[part] = generate_bassline(key, tempo, time_signature, measures, name_part, part, chord_progression, melody)
        beat_filename[part] = generate_beat(tempo, time_signature, measures, name_part, part, beat_pat_file)
    return harm_filename, bass_filename, melo_filename, beat_filename

def generate_song_arrangement() :
    common_structures = [
        ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus'],
        ['chorus', 'verse', 'chorus', 'bridge', 'verse', 'chorus'],
        ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'],
        ['verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'outro'],
        ['intro', 'verse', 'chorus', 'bridge', 'verse', 'chorus'],
        ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus'],
        ['intro', 'verse', 'chorus', 'bridge', 'chorus'],
        ['intro', 'verse', 'chorus', 'outro'],
        ['verse', 'chorus', 'outro'],
        ['chorus', 'verse', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'outro'],
        ['verse', 'chorus', 'outro'],
        ['chorus', 'verse', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['chorus', 'verse', 'chorus', 'bridge', 'verse', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'bridge', 'verse', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'bridge', 'chorus'],
        ['intro', 'verse', 'bridge', 'chorus', 'verse', 'chorus', 'outro'],
        ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus', 'outro']
    ]
    result = random.choice(common_structures)
    unique_elements = list(set(result))
    return unique_elements, result

def read_instrument_probabilities(file_path):
    with open(file_path) as f:
        inst_probabilities = json.load(f)
    return inst_probabilities  

def get_random_sound_font(directory_path):
    sound_fonts = [f for f in os.listdir(directory_path) if f.endswith('.sf2')]
    file_return = random.choice(sound_fonts)
    return os.path.join(directory_path, file_return)

def get_levels(file_path):
    with open(file_path) as f:
        levels = json.load(f)
    return levels  

def create_effect(effect_class, parameters):
    # Unpack the parameters
    probability = parameters['probability']
    value_range = parameters['value_range']
    
    if random.random() < probability:
        kwargs = {param: random.uniform(value_range[param][0], value_range[param][1])
                  for param in value_range}
        return effect_class(**kwargs)
    return None

def generate_pedalboard(effect_params_file):
    # Load effect parameters from the JSON file
    with open(effect_params_file, 'r') as json_file:
        effect_params = json.load(json_file)
    # Create a list of effects with their respective probabilities and value ranges
    effects = [
        (Compressor, effect_params['compressor']),
        (Gain, effect_params['gain']),
        (Chorus, effect_params['chorus']),
        (LadderFilter, effect_params['ladder_filter']),
        (Phaser, effect_params['phaser']),
        (Delay, effect_params['delay']),
        (Reverb, effect_params['reverb']),
    ]
    
    # Create a new pedalboard with the specified effects
    board = Pedalboard([effect for effect in (create_effect(effect_class, parameters)
                                          for effect_class, parameters in effects)
                    if effect is not None])
    return board
    
def apply_fx_to_layer(wav_file, board):
    # Apply the pedalboard effects to the input file        
    with AudioFile(wav_file) as af:
        with AudioFile(wav_file+'_fx.wav', 'w', af.samplerate, af.num_channels) as of:        
            while af.tell() < af.frames:
                chunk = af.read(af.samplerate)
                effected = board(chunk, af.samplerate, reset=False)
                of.write(effected)
              
    return wav_file+'_fx.wav'

def pedalboard_info_json(board):
    pedals_and_parameters = []
    for pedal in board:
        attributes = dir(pedal)

        # Filter out the attributes that are not parameters
        parameters = [attr for attr in attributes if not attr.startswith("_") and not callable(getattr(pedal, attr))]
        
        pedal_info = {
            "name": pedal.__class__.__name__,
            "parameters": {}
        }
        
        for parameter in parameters:
            value = getattr(pedal, parameter)
            pedal_info['parameters'][str(parameter)] = str(value)               
        pedals_and_parameters.append(pedal_info)    
    return pedals_and_parameters
    
# Mix song parts and save the result to WAV files
def mix_and_save(harm_filename, bass_filename, melo_filename, beat_filename, name):
    # TODO: only render and mix the parts that are used in the song arrangement
    song_unique_parts, song_arrangement = generate_song_arrangement()
    print("Song arrangement: "+ str(song_arrangement) + "\n")
    number_of_parts = len(song_arrangement)
    song_parts = []
    part_layers = {}
    part_layers['intro'] = []
    part_layers['verse'] = []
    part_layers['chorus'] = []
    part_layers['bridge'] = []
    part_layers['outro'] = []
    part_counter = 0
    soundfonts = {}
    pedalboards = {}
    #TODO: configure soundfont directory 
    beat_soundfont = get_random_sound_font(str(os.path.join('sf','beat')))
    melody_soundfont = get_random_sound_font(str(os.path.join('sf','melody')))
    harmony_soundfont = get_random_sound_font(str(os.path.join('sf','harmony')))
    bassline_soundfont = get_random_sound_font(str(os.path.join('sf','bassline')))
    soundfonts['beat'] = beat_soundfont
    soundfonts['melody'] = melody_soundfont
    soundfonts['harmony'] = harmony_soundfont
    soundfonts['bassline'] = bassline_soundfont    
    print("Beat soundfont: " + beat_soundfont)
    print("Melody soundfont: " + melody_soundfont)
    print("Harmony soundfont: " + harmony_soundfont)
    print("Bassline soundfont: " + bassline_soundfont)
    beat_board = generate_pedalboard('beat_fx.json')
    melody_board = generate_pedalboard('melody_fx.json')
    harmony_board = generate_pedalboard('harmony_fx.json')
    bassline_board = generate_pedalboard('bassline_fx.json')    
    pedalboards['beat'] = pedalboard_info_json(beat_board)
    pedalboards['melody'] = pedalboard_info_json(melody_board)
    pedalboards['harmony'] = pedalboard_info_json(harmony_board)
    pedalboards['bassline'] = pedalboard_info_json(bassline_board)
    print("Beat pedalboard: " + str(beat_board))
    print("Melody pedalboard: " + str(melody_board))
    print("Harmony pedalboard: " + str(harmony_board))
    print("Bassline pedalboard: " + str(bassline_board))
    # TODO: gather all file references in a single config file
    inst_proba = read_instrument_probabilities('inst_probabilities.json')
    levels = {}
    levels = get_levels('levels.json')
    print("Levels: " + str(levels))
    beat_part_mix = {}
    melody_part_mix = {}
    harmony_part_mix = {}
    bassline_part_mix = {}
    # Define which layers will be used for each part
    for part in song_unique_parts:
        beat_proba = float(inst_proba[part]['beat'])
        melody_proba = float(inst_proba[part]['melody'])
        harmony_proba = float(inst_proba[part]['harmony'])
        bassline_proba = float(inst_proba[part]['bassline'])
        beat_part_mix[part] = (random.random() <= beat_proba) 
        melody_part_mix[part] = (random.random() <= melody_proba)
        harmony_part_mix[part] = (random.random() <= harmony_proba)
        bassline_part_mix[part] = (random.random() <= bassline_proba)    
    print("Mixing song parts...")
    song_transitions = []
    song_time = 0
    for part in song_arrangement:
        this_transition = [part, song_time]
        song_transitions.append(this_transition)
        part_counter += 1
        print("Mixing part: " + part + (' (' + str(part_counter) + ' of ' + str(number_of_parts) + ')'))        
        # Render each MIDI file to an audio file using the chosen soundfont
        beat_wav = 'beat' + "-" + str(part_counter) + "-" + part + ".wav"
        beat_wav = os.path.join(name, beat_wav)
        FluidSynth(beat_soundfont).midi_to_audio(beat_filename[part], beat_wav)
        melo_wav = 'melody' + "-" + str(part_counter) + "-" + part + ".wav"
        melo_wav = os.path.join(name, melo_wav)
        FluidSynth(melody_soundfont).midi_to_audio(melo_filename[part], melo_wav)
        harm_wav = 'harmony' + "-" + str(part_counter) + "-" + part + ".wav"
        harm_wav = os.path.join(name, harm_wav)
        FluidSynth(harmony_soundfont).midi_to_audio(harm_filename[part], harm_wav)
        bass_wav = 'bassline' + "-" + str(part_counter) + "-" + part + ".wav"
        bass_wav = os.path.join(name, bass_wav)
        FluidSynth(bassline_soundfont).midi_to_audio(bass_filename[part], bass_wav)
        # Load the rendered audio files, applying the effects defined in the JSON files
        # TODO: optimize it so that the fx are only applied to the used layers
        beat = AudioSegment.from_wav(apply_fx_to_layer(beat_wav, beat_board))
        melody = AudioSegment.from_wav(apply_fx_to_layer(melo_wav, melody_board))
        harmony = AudioSegment.from_wav(apply_fx_to_layer(harm_wav, harmony_board))
        bassline = AudioSegment.from_wav(apply_fx_to_layer(bass_wav, bassline_board))
        # Volume and panning for each layer
        beat.volume = float(levels[part]['beat']['volume'])
        melody.volume = float(levels[part]['melody']['volume'])
        harmony.volume = float(levels[part]['harmony']['volume'])
        bassline.volume = float(levels[part]['bassline']['volume'])
        beat.pan(float(levels[part]['beat']['panning']))
        melody.pan(float(levels[part]['melody']['panning']))
        harmony.pan(float(levels[part]['harmony']['panning']))
        bassline.pan(float(levels[part]['bassline']['panning']))      
        # Create an empty AudioSegment to use as the initial mix
        mix = AudioSegment.silent(duration=beat.duration_seconds*1000)
        # Overlay each track onto the mix based on its probability value        
        # TODO: if layer is chosen, apply effects (considering probability) and mix
        # TODO: create a data structure to store which layers are used in each part
        # Mix the audio files together
        if beat_part_mix[part]:
            mix = mix.overlay(beat)
            if 'beat' not in part_layers[part]:
                part_layers[part].append('beat')
            print("Beat added to mix: "+part)
        if melody_part_mix[part]:
            mix = mix.overlay(melody)
            if 'melody' not in part_layers[part]:
                part_layers[part].append('melody')
            print("Melody added to mix: "+part)
        if harmony_part_mix[part]:
            mix = mix.overlay(harmony)  
            if 'harmony' not in part_layers[part]:
                part_layers[part].append('harmony')         
            print("Harmony added to mix: "+part)
        if bassline_part_mix[part]:
            mix = mix.overlay(bassline)
            if 'bassline' not in part_layers[part]:
                part_layers[part].append('bassline')
            print("Bassline added to mix: "+part)
        # Save the mixed audio to the output file
        part_mix_file = name + '-' + str(part_counter) + '.wav'
        part_mix_file = os.path.join(name, part_mix_file) 
        mix.export(part_mix_file, format='wav')
        song_parts.append(part_mix_file)
        song_time = song_time + mix.duration_seconds
    
    this_transition = ['end', song_time]
    song_transitions.append(this_transition)
    # Iterate through song_parts and concatenate them into a single file
    song = AudioSegment.from_wav(song_parts[0])
    for part_wav in song_parts[1:]:
        song += AudioSegment.from_wav(part_wav)
    # Save the song as a wav file
    song_file_wav = name + '.wav'
    song_file_wav = os.path.join(name, song_file_wav)
    song.export(song_file_wav, format='wav')
    print("Song saved as: " + song_file_wav)
    # Clean the wav parts
    for part_wav in song_parts:
        os.remove(part_wav)
        
    return song_file_wav, song_arrangement, song_transitions, soundfonts, pedalboards, part_layers

# Create song file and metadata
def create_song(key, tempo, time_signature, measures, name, chord_pat_file, beat_pat_file):
    song_info = {}
    song_info['key'] = key
    song_info['tempo'] = tempo
    song_info['time_signature'] = time_signature
    song_info['measures'] = measures
    song_info['name'] = name

    ha = {}
    ba = {}
    me = {}
    be = {}

    song_name = name

    start_time = time.time()
    
    ha, ba, me, be = generate_song_parts(key, tempo, time_signature, measures, song_name, chord_pat_file, beat_pat_file)
    wav_name, arrangement, transitions, soundfonts, pedalboards, part_layers = mix_and_save(ha, ba, me, be, song_name)
    
    end_time = time.time()
    
    song_info['file_name'] = wav_name
    song_info['arrangement'] = arrangement
    song_info['transitions'] = transitions
    song_info['soundfonts'] = soundfonts
    song_info['pedalboards'] = pedalboards
    song_info['part_layers'] = part_layers
    song_info['musicality_score'] = musicality_score.get_musicality_score(wav_name)
    
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.2f} seconds')
    print(f'Musicality score: {song_info["musicality_score"]:.2f}')
    
    json_file = os.path.join(name, name + '.json')
    
    print('Annotations: ' + json_file)
    
    with open(json_file, 'w') as outfile:
        json.dump(song_info, outfile, indent=4)

    # TODO: clean temp files in a better way (ATS)
    # TODO generate stems for each layer / the whole song
    midi_del = "*.mid"
    midi_path = os.path.join(name, midi_del)
    midi_files = glob.glob(midi_path)
    # for midi_file in midi_files:
        # os.remove(midi_file)
    
    wav_del = "beat-*.wav" 
    wav_path = os.path.join(name, wav_del)
    wav_files = glob.glob(wav_path)
    # for wav_file in wav_files:
        # os.remove(wav_file)

    wav_del = "bassline-*.wav" 
    wav_path = os.path.join(name, wav_del)
    wav_files = glob.glob(wav_path)
    # for wav_file in wav_files:
        # os.remove(wav_file)

    wav_del = "harmony-*.wav" 
    wav_path = os.path.join(name, wav_del)
    wav_files = glob.glob(wav_path)
    # for wav_file in wav_files:
        # os.remove(wav_file)

    wav_del = "melody-*.wav" 
    wav_path = os.path.join(name, wav_del)
    wav_files = glob.glob(wav_path)
    # for wav_file in wav_files:
        # os.remove(wav_file)

    
    return wav_name, json_file

def generate_random_key():
    # https://www.digitaltrends.com/music/whats-the-most-popular-music-key-spotify/
    # https://web.archive.org/web/20190426230344/https://insights.spotify.com/us/2015/05/06/most-popular-keys-on-spotify/
    # https://forum.bassbuzz.com/t/most-used-keys-on-spotify/5886

    key_ranges = [(0.107, 'G'), (0.209, 'C'), (0.296, 'D'), (0.357, 'A'), (0.417, 'C#'), (0.47, 'F'),
                  (0.518, 'Am'), (0.561, 'G#'), (0.603, 'Em'), (0.645, 'Bm'), (0.681, 'E'), (0.716, 'A#'),
                  (0.748, 'A#m'), (0.778, 'Fm'), (0.805, 'F#'), (0.831, 'B'), (0.857, 'Gm'), (0.883, 'Dm'),
                  (0.908, 'F#m'), (0.932, 'D#'), (0.956, 'Cm'), (0.977, 'C#m'), (0.989, 'G#m'), (1.0, 'D#m')
    ]
    dice = random.random()
    for prob, key in key_ranges:
        if dice < prob:
            return key    

def generate_random_tempo():
    # https://blog.musiio.com/2021/08/19/which-musical-tempos-are-people-streaming-the-most/
    tempo_ranges = [(0.0183, 60, 70), (0.0454, 70, 80), (0.1849, 80, 90), (0.3721, 90, 100),
                    (0.4817, 100, 110), (0.5747, 110, 120), (0.7048, 120, 130), (0.7917, 130, 140),
                    (0.8958, 140, 150), (0.9739, 150, 160), (1.0, 160, 170)]
    dice = random.random()
    for prob, min_tempo, max_tempo in tempo_ranges:
        if dice < prob:
            return random.randint(min_tempo, max_tempo)

def generate_random_time_signature():
    time_signature_ranges = [(0.6, '4/4'), (0.75, '3/4'), (0.90, '2/4'), (1.0, '6/8')]
    dice = random.random()
    for prob, time_signature in time_signature_ranges:
        if dice < prob:
            return time_signature  

def generate_song_measures():
    intro_len = random.choice([8, 16, 32])
    verse_len = random.choice([16, 32, 32, 64]) # Repeated to emphasize more common verse lengths
    chorus_len = random.choice([16,32])
    bridge_len = random.choice([8, 16, 16, 32]) # Repeated to emphasize more common bridge lengths
    outro_len = random.choice([8,16,32])
    song_measures = {
        'intro': intro_len,
        'verse': verse_len,
        'chorus': chorus_len,
        'bridge': bridge_len,
        'outro': outro_len
    }
    return song_measures

# Example usage

for i in range(10):
    key = generate_random_key()
    tempo = generate_random_tempo()
    time_signature = generate_random_time_signature()
    song_measures = generate_song_measures()
    now = datetime.now()
    song_name = now.strftime("%Y%m%d%H%M%S")
    create_song(key, tempo, time_signature, song_measures, song_name, 'chord_patterns.txt', 'beat_roll_patterns.txt')
