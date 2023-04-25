from midiutil import MIDIFile
from music21 import *
import random

def generate_melody(key, tempo, time_signature, measures):
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
    with open("melody.mid", 'wb') as outf:
        mf.writeFile(outf)


# Example usage
generate_melody('C', 120, '4/4', 8)
