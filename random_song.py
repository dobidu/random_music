from midiutil import MIDIFile
from music21 import *
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
    return chord_pattern

def generate_bassline(key, tempo, time_signature, measures, name, part, chord_progression):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Bassline")
    mf.addTempo(track, time, tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Create a bassline
    bassline = []
    note_durations = []
    total_notes = measures * beats_per_measure

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

    while total_notes > 0:
        # Choose a random note and duration
        note_name = random.choice(notes_to_use)
        note_duration = random.choice([1, 2])
        if note_duration > total_notes:
            note_duration = total_notes

        # Add note to bassline
        note = pitch.Pitch(note_name.name)
        note.octave = 2
        bassline.append(note)
        note_durations.append(note_duration)

        total_notes -= note_duration

    # Add notes to MIDI file
    for i in range(len(bassline)):
        note = bassline[i]
        note_duration = note_durations[i]
        velocity = random.randint(70, 100)
        mf.addNote(track, 0, note.midi, time, note_duration, velocity)
        time += note_duration

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-bassline.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
    
def generate_melody(key, tempo, time_signature, measures, name, part, chord_progression):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Melody")
    mf.addTempo(track, time, tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Create a melody
    melody = []
    note_durations = []
    total_notes = measures * beats_per_measure

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

    while total_notes > 0:
        # Choose a random note and duration
        note_name = random.choice(notes_to_use)
        note_duration = random.choice([1, 2])
        if note_duration > total_notes:
            note_duration = total_notes

        # Add note to melody
        note = pitch.Pitch(note_name.name)
        melody.append(note)
        note_durations.append(note_duration)

        total_notes -= note_duration

    # Add notes to MIDI file
    for i in range(len(melody)):
        note = melody[i]
        note_duration = note_durations[i]
        velocity = random.randint(70, 100)
        mf.addNote(track, 0, note.midi, time, note_duration, velocity)
        time += note_duration

    # Save MIDI file
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, name + "-melody.mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)


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

def generate_song_parts(key, tempo, time_signature, song_structure, name, chord_pat_file, beat_pat_file):
    print("Generating song parts for: " + name)
    print("\tKey: " + key)
    print("\tTempo: " + str(tempo))
    print("\tTime signature: " + time_signature)
    for part, measures in song_structure.items():
        print("\t\tGenerating part: " + part + " (" + str(measures) + " measures)")
        name_part = name + "-" + part
        chord_progression = generate_chord_progression(key, tempo, time_signature, measures, name_part, part, chord_pat_file)
        generate_bassline(key, tempo, time_signature, measures, name_part, part, chord_progression)
        generate_melody(key, tempo, time_signature, measures, name_part, part, chord_progression)
        generate_beat(tempo, time_signature, measures, name_part, part, beat_pat_file)

# Example usage

# TODO: add a second data structure
# to define different arrangements for the parts

song_structure1 = {
    'intro': 4,
    'verse': 8,
    'chorus': 8,
    'bridge': 4,
    'outro': 4
}
generate_song_parts('C', 120, '4/4', song_structure1, 'song1', 'chord_patterns.txt', 'beat_patterns.txt')

song_structure2 = {
    'intro': 2,
    'verse': 16,
    'chorus': 8,
    'bridge': 8,
    'outro': 2
}
song2 = generate_song_parts('G', 100, '3/4', song_structure2, 'song2', 'chord_patterns.txt', 'beat_patterns.txt')
