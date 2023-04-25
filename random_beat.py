from midiutil import MIDIFile
import random

def generate_beat(tempo, time_signature, measures):
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
    with open("beat.mid", 'wb') as outf:
        mf.writeFile(outf)

# Example usage
generate_beat(120, '4/4', 8)