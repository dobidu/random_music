from midiutil import MIDIFile
from music21 import *
import random

def generate_chord_progression(key, tempo, time_signature, measures, name):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Chord Progression")
    mf.addTempo(track, time, tempo)
    
    beats_per_measure = int(time_signature.split('/')[0])

    #TODO: read from file, increase number of chord patterns
    chord_progression = []
    chord_pattern = random.choice([
            ['I', 'IV', 'V', 'vi'],
            ['ii', 'V', 'I'],
            ['I', 'vi', 'IV', 'V'],
            ['I', 'IV', 'vi', 'V']
        ])
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
    with open(name + "-chord_progression.mid", 'wb') as outf:
        mf.writeFile(outf)


def generate_beat(tempo, time_signature, measures, name):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Beat")
    mf.addTempo(track, time, tempo)

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Define drum sounds
    kick = 36
    snare = 38
    hihat = 42

    # Create a beat
    beat = []
    for i in range(measures):
        # Choose a random beat pattern based on common beat patterns
        beat_pattern = random.choice([
            [kick, 0, snare, 0],
            [kick, 0, snare, hihat],
            [kick, hihat, snare, hihat],
            [kick, hihat, kick, snare]
        ])
        beat.extend(beat_pattern)

    # Add notes to MIDI file
    for i in range(len(beat)):
        drum_sound = beat[i]
        if drum_sound != 0:
            mf.addNote(track, 9, drum_sound, time, 1.0 / beats_per_measure, 100)
        time += 1.0 / beats_per_measure

    # Save MIDI file
    with open(name + "-beat.mid", 'wb') as outf:
        mf.writeFile(outf)


def generate_bassline(key, tempo, time_signature, measures, name):
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

    while total_notes > 0:
        # Choose a random note and duration
        note_name = random.choice(scale_obj.getPitches())
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
    with open(name + "-bassline.mid", 'wb') as outf:
        mf.writeFile(outf)

def generate_melody(key, tempo, time_signature, measures, name):
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

    while total_notes > 0:
        # Choose a random note and duration
        note_name = random.choice(scale_obj.getPitches())
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
    with open(name + "-melody.mid", 'wb') as outf:
        mf.writeFile(outf)

def generate_song(key, tempo, time_signature, song_structure, name):
    for part, measures in song_structure.items():
        part_name = name + "-" + part;
        generate_chord_progression(key, tempo, time_signature, measures, part_name)
        generate_bassline(key, tempo, time_signature, measures, part_name)
        generate_melody(key, tempo, time_signature, measures, part_name)
        generate_beat(tempo, time_signature, measures, part_name)

# Example usage

song_structure1 = {
    'intro': 4,
    'verse': 8,
    'chorus': 8,
    'bridge': 4,
    'outro': 4
}
generate_song('C', 120, '4/4', song_structure1, "song1")

song_structure2 = {
    'intro': 2,
    'verse': 16,
    'chorus': 8,
    'bridge': 8,
    'outro': 2
}
song2 = generate_song('G', 100, '3/4', song_structure2, "song2")