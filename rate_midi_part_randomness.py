import mido
from music21 import *

def rate_randomness(mid, part):
    # Extract notes and chords from MIDI file
    mf = midi.translate.midiFileToMusic21Object(mid)
    score = mf.makeNotation()
    notes = []
    chords = []
    for element in score.recurse():
        if isinstance(element, note.Note):
            notes.append(element)
        elif isinstance(element, chord.Chord):
            chords.append(element)
    
    # Calculate repetition score
    repetition_score = 0
    for i in range(len(notes) - 1):
        if notes[i].nameWithOctave == notes[i + 1].nameWithOctave:
            repetition_score += 1
    repetition_score = repetition_score / len(notes)
    
    # Calculate harmony score
    harmony_score = 0
    for c in chords:
        if c.isConsonant():
            harmony_score += 1
    harmony_score = harmony_score / len(chords)
    
    # Calculate melody score
    melody_score = 0
    for i in range(len(notes) - 1):
        interval = interval.Interval(noteStart=notes[i], noteEnd=notes[i + 1])
        if interval.name in ['P1', 'm2', 'M2', 'm3', 'M3']:
            melody_score += 1
    melody_score = melody_score / len(notes)
    
    # Calculate rhythm score
    rhythm_score = 0
    for n in notes:
        if n.duration.quarterLength in [0.25, 0.5, 1.0, 2.0]:
            rhythm_score += 1
    rhythm_score = rhythm_score / len(notes)
    
    # Combine scores (magic numbers extravaganza)
    if part == 'intro':
        randomness = 1 - (repetition_score * 0.2 + harmony_score * 0.4 + melody_score * 0.2 + rhythm_score * 0.2)
    elif part == 'verse':
        randomness = 1 - (repetition_score * 0.3 + harmony_score * 0.3 + melody_score * 0.2 + rhythm_score * 0.2)
    elif part == 'chorus':
        randomness = 1 - (repetition_score * 0.4 + harmony_score * 0.2 + melody_score * 0.2 + rhythm_score * 0.2)
    elif part == 'bridge':
        randomness = 1 - (repetition_score * 0.2 + harmony_score * 0.3 + melody_score * 0.3 + rhythm_score * 0.2)
    elif part == 'outro':
        randomness = 1 - (repetition_score * 0.3 + harmony_score * 0.3 + melody_score * 0.2 + rhythm_score * 0.2)
    
    return randomness

# Load MIDI file
mid = mido.MidiFile('example.mid')

# Rate randomness for each part
parts = ['intro', 'verse', 'chorus', 'bridge', 'outro']
for part in parts:
    randomness = rate_randomness(mid, part)
    print(f'{part.capitalize()} randomness: {randomness}')
