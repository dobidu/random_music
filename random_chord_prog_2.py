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

    # Determine the number of beats per measure based on the time signature
    beats_per_measure = int(time_signature.split('/')[0])

    # Create a chord progression
    chord_progression = []
    chord_durations = []
    total_chords = measures * beats_per_measure
    while total_chords > 0:
        # Choose a random chord symbol and duration
        chord_symbol = random.choice(['I', 'IV', 'V', 'vi', 'ii'])
        chord_duration = random.choice([1, 2])
        if chord_duration > total_chords:
            chord_duration = total_chords

        # Add chord to progression
        chord = roman.RomanNumeral(chord_symbol, key)
        chord_progression.append(chord)
        chord_durations.append(chord_duration)

        total_chords -= chord_duration

    # Add chords to MIDI file
    for i in range(len(chord_progression)):
        chord = chord_progression[i]
        chord_duration = chord_durations[i]
        for note in chord.pitches:
            mf.addNote(track, 0, note.midi, time, chord_duration, 100)
        time += chord_duration

    # Save MIDI file
    with open("chord_progression.mid", 'wb') as outf:
        mf.writeFile(outf)

# Example usage
generate_chord_progression('C', 120, '4/4', 8)