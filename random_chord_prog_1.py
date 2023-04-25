from midiutil import MIDIFile
from music21 import *
import random

def generate_chord_progression(key, tempo, time_signature, measures):
    # Create a MIDI file with one track
    mf = MIDIFile(1)
    track = 0
    time = 0
    mf.addTrackName(track, time, "Chord Progression")
    mf.addTempo(track, time, tempo)
    
    beats_per_measure = int(time_signature.split('/')[0])

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
    # Add chords to MIDI file
    # for chord in chord_progression:
    #    for note in chord.pitches:
    #        mf.addNote(track, 0, note.midi, time, chord_duration, 100)
    #    # time += 1
    #    time += chord_duration

    # Save MIDI file
    with open("chord_progression.mid", 'wb') as outf:
        mf.writeFile(outf)

# Example usage
generate_chord_progression('D', 120, '4/4', 4)