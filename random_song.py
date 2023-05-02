from midiutil import MIDIFile
from music21 import *
from pydub import AudioSegment
from midi2audio import FluidSynth
import random
import os

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

def generate_bassline(key, tempo, time_signature, measures, name, part, chord_progression):
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
    elif part == 'outro':
        notes_to_use = [chords[-1].pitches[0]]
    else:
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
            transition_matrix[note.midi][next_note.midi] = 1 / len(notes_to_use)
    
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
    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-melody.mid")
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
    if part in beat_patterns:
        beat_pattern = random.choice(beat_patterns[part])
    else:
        beat_pattern = [kick ,0 ,snare ,0]
    for i in range(measures):
        # Choose a random beat pattern based on song part and available patterns from file
        beat.extend(beat_pattern)

    # Add notes to MIDI file
    for i in range(len(beat)):
        drum_sound =beat[i]
        if drum_sound !=0:
            mf.addNote(track ,9 ,drum_sound ,time ,1.0/beats_per_measure ,100)
        time +=1.0/beats_per_measure

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-beat.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
    
    print("\t\t\tBeat: " + str(beat_pattern))
    return filename

def generate_song_parts(key, tempo, time_signature, song_structure, name, chord_pat_file, beat_pat_file):
    print("Generating song parts for: " + name)
    print("\tKey: " + key)
    print("\tTempo: " + str(tempo))
    print("\tTime signature: " + time_signature)
    harm_filename = {}
    bass_filename = {}
    melo_filename = {}
    beat_filename = {}
    for part, measures in song_structure.items():
        print("\t\tGenerating part: " + part + " (" + str(measures) + " measures)")
        name_part = name + "-" + part
        chord_progression, harm_filename[part] = generate_chord_progression(key, tempo, time_signature, measures, name_part, part, chord_pat_file)
        bass_filename[part] = generate_bassline(key, tempo, time_signature, measures, name_part, part, chord_progression)
        melo_filename[part] = generate_melody(key, tempo, time_signature, measures, name_part, part, chord_progression)
        beat_filename[part] = generate_beat(tempo, time_signature, measures, name_part, part, beat_pat_file)
    return harm_filename, bass_filename, melo_filename, beat_filename

def generate_song_arrangement() :
    common_structures = [
        ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
        ['verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus'],
        ['chorus', 'verse', 'chorus', 'bridge', 'verse', 'chorus'],
        ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'],
        ['verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus'],
        ['intro', 'verse', 'chorus', 'bridge', 'verse', 'chorus'],
        ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus'],
        ['intro', 'verse', 'chorus', 'bridge','chorus'],
        ['intro','verse','bridge','chorus','verse','chorus','outro'],
        ['intro','verse','chorus','verse','bridge','chorus','outro']
    ]
    return random.choice(common_structures)

def mix_and_save(harm_filename, bass_filename, melo_filename, beat_filename, name):
    song_arramgement = generate_song_arrangement()
    print("Song arrangement: "+ str(song_arramgement) + "\n")
    number_of_parts = len(song_arramgement)
    # exit(0)
    song_parts = []
    part_counter = 0
    # TODO: Choose a random soundfont for each layer from pattern file
    beat_soundfont = os.path.join('sf','some_drum.sf2')
    melody_soundfont = os.path.join('sf', 'JR_elepiano.sf2')
    harmony_soundfont = os.path.join('sf','JR_organ.sf2')
    bassline_soundfont = os.path.join('sf','Genycis_Dark_Stage_Bass.sf2')

    for part in song_arramgement:
        part_counter += 1        
        print("Mixing part: " + part + (' (' + str(part_counter) + ' of ' + str(number_of_parts) + ')'))        
        # Render each MIDI file to an audio file using the chosen soundfont
        beat_wav = 'beat' + "-" + part + "-" + str(part_counter) + ".wav"
        beat_wav = os.path.join(name, beat_wav)
        FluidSynth(beat_soundfont).midi_to_audio(beat_filename[part], beat_wav)
        melo_wav = 'melody' + "-" + part + "-" + str(part_counter) + ".wav"
        melo_wav = os.path.join(name, melo_wav)
        FluidSynth(melody_soundfont).midi_to_audio(melo_filename[part], melo_wav)
        harm_wav = 'harmony' + "-" + part + "-" + str(part_counter) + ".wav"
        harm_wav = os.path.join(name, harm_wav)
        FluidSynth(harmony_soundfont).midi_to_audio(harm_filename[part], harm_wav)
        bass_wav = 'bassline' + "-" + part + "-" + str(part_counter) + ".wav"
        bass_wav = os.path.join(name, bass_wav)
        FluidSynth(bassline_soundfont).midi_to_audio(bass_filename[part], bass_wav)
        # Load the rendered audio files
        beat = AudioSegment.from_wav(beat_wav)
        melody = AudioSegment.from_wav(melo_wav)
        harmony = AudioSegment.from_wav(harm_wav)
        bassline = AudioSegment.from_wav(bass_wav)
        #TODO: volume and panning for each layer
        
        # Mix the audio files together
        mix = beat.overlay(melody).overlay(harmony).overlay(bassline)
        
        # Save the mixed audio to the output file
        part_mix_file = name + '-' + str(part_counter) + '.wav';
        part_mix_file = os.path.join(name, part_mix_file) 
        mix.export(part_mix_file, format='wav')
        song_parts.append(part_mix_file)
    
    # Iterate through song_parts and concatenate them into a single file
    song = AudioSegment.from_wav(song_parts[0])
    for part_wav in song_parts[1:]:
        song += AudioSegment.from_wav(part_wav)
    # Save the song as a wav file
    song_file_wav = name + '.wav'
    song_file_wav = os.path.join(name, song_file_wav)
    song.export(song_file_wav, format='wav')
    print("Song saved as: " + song_file_wav)
    return song_file_wav
        
song_structure1 = {
    'intro': 4,
    'verse': 8,
    'chorus': 8,
    'bridge': 4,
    'outro': 4
}

ha = {}
ba = {}
me = {}
be = {}

ha, ba, me, be = generate_song_parts('C', 90, '4/4', song_structure1, 'song2', 'chord_patterns.txt', 'beat_patterns.txt')
mix_and_save(ha, ba, me, be, 'song2')

song_structure2 = {
    'intro': 2,
    'verse': 16,
    'chorus': 8,
    'bridge': 8,
    'outro': 2
}
# song2 = generate_song_parts('G', 100, '3/4', song_structure2, 'song2', 'chord_patterns.txt', 'beat_patterns.txt')
