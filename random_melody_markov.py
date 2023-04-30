from midiutil import MIDIFile
from music21 import *
import random

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
    with open(name + "-melody.mid", 'wb') as outf:
        mf.writeFile(outf)

# Example usage

generate_melody('Cm', 120, '4/4', 8, "test3", "chorus", ["i", "iv", "v", "i"])