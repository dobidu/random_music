from midiutil import MIDIFile
from music21 import scale, roman
from pydub import AudioSegment
from midi2audio import FluidSynth
from pedalboard import Pedalboard, Compressor, Gain, Chorus, LadderFilter, Phaser, Delay, Reverb
from pedalboard.io import AudioFile

import json
import random
import os
import time
from datetime import datetime

def generate_beat(tempo, time_signature, measures, name, beat_parts):
    # Mapeamento MIDI completo para partes de bateria
    drum_mapping = {
        'kick': [35, 36],  # Notas MIDI para o bumbo
        'snare': [38, 40],  # Notas MIDI para a caixa
        'hihat': [42, 44, 46],  # Notas MIDI para o chimbal
        'tom_low': [41, 43, 45],  # Notas MIDI para o tom baixo
        'tom_mid': [47, 48],  # Notas MIDI para o tom médio
        'tom_high': [50, 51],  # Notas MIDI para o tom alto
        'cymbal': [49, 52, 55, 57, 59],  # Notas MIDI para os pratos
        'ride': [51, 53, 59],  # Notas MIDI para o ride
        'clap': [39, 75],  # Notas MIDI para as palmas
        'perc': [54, 56, 58, 60, 62, 64, 65, 66, 68, 70, 72, 74, 76, 77, 78]  # Notas MIDI para percussão
    }

    # Crie um arquivo MIDI para cada parte da batida
    mfs = {part: MIDIFile(1) for part in beat_parts}
    track = 0
    time = 0

    for part, mf in mfs.items():
        mf.addTrackName(track, time, part)
        mf.addTempo(track, time, tempo)

    # Determine o número de batidas por medida com base na assinatura de tempo
    beats_per_measure = int(time_signature.split('/')[0])
    beat_duration = 60 / tempo  # Duration of a single beat in seconds
    measure_duration = beats_per_measure * beat_duration  # Duration of a measure in seconds
    total_duration = measures * measure_duration  # Total duration in seconds    
    
    # Gere uma batida aleatória para cada parte
    beats = {part: [] for part in beat_parts}
    note_durations = {part: [] for part in beat_parts}

    for part in beat_parts:
        total_notes = measures * beats_per_measure

        while total_notes > 0:
            # Escolha uma nota MIDI aleatória para a parte da bateria
            current_note = random.choice(drum_mapping[part])

            # Escolha uma duração aleatória para a nota
            note_duration = random.choice([1, 2])
            if note_duration > total_notes:
                note_duration = total_notes

            # Adicione a nota à batida
            beats[part].append(current_note)
            note_durations[part].append(note_duration)
            total_notes -= note_duration

    # Adicione notas ao arquivo MIDI
    for part, mf in mfs.items():
        time = 0
        for i in range(len(beats[part])):
            note = beats[part][i]
            note_duration = note_durations[part][i]
            velocity = random.randint(70, 100)
            mf.addNote(track, 0, note, time, note_duration, velocity)
            time += note_duration

    print("\t\t\tBeats: ", beats)

    # Salve cada arquivo MIDI
    directory = name.split('-')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)

    filenames = {}
    for part, mf in mfs.items():
        filename = os.path.join(directory, f"{name}-{part}.mid")
        with open(filename, 'wb') as outf:
            mf.writeFile(outf)
        filenames[part] = filename

    return beats, filenames, total_duration

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


def get_random_sound_font(directory_path):
    sound_fonts = [f for f in os.listdir(directory_path) if f.endswith('.sf2')]
    file_return = random.choice(sound_fonts)
    return os.path.join(directory_path, file_return)

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

def generate_beat_elements():
    all_parts_ranges = [(0.95, 'kick'), (0.85, 'snare'), (0.7, 'hihat'), 
                        (0.4, 'tom_low'), (0.4, 'tom_mid'), (0.4, 'tom_high'), 
                        (0.3, 'cymbal'), (0.3, 'ride'), (0.3, 'clap'), (0.2, 'perc')]
    selected_ranges = []
    # dice = random.random()
    for prob, element in all_parts_ranges:
        dice = random.random()
        if dice < prob:
            selected_ranges.append(element)
    return selected_ranges
    

def generate_beat_size():
    return random.choice([8, 16, 32])

def get_beat_part_level(beat_part):
    part_ranges = [('kick', 0.5, 0.9), ('snare', 0.4, 0.8), ('hihat', 0.4, 0.8),
                   ('tom_high', 0.3, 0.8), ('tom_mid', 0.3, 0.8), ('tom_low', 0.3, 0.8),
                   ('cymbal', 0.3, 0.8), ('ride', 0.5, 0.9), ('clap', 0.4, 0.8), 
                   ('perc', 0.4, 0.7)]
    
    for part, range_max, range_min in part_ranges:
        if part == beat_part:
            return random.uniform(range_min, range_max)
        
def get_beat_part_pan(beat_part):
    part_ranges = [('kick', 0.0, 0.0), ('snare', -0.1, 0.1), ('hihat', -0.2, 0.2),
                   ('tom_high', -0.5, -0.2), ('tom_mid', -0.1, 0.3), ('tom_low', 0.3, 0.8),
                   ('cymbal', -0.8, -0.3), ('ride', 0.3, 0.9), ('clap', -0.1, 0.1), 
                   ('perc', -0.9, 0.9)]
    
    for part, range_max, range_min in part_ranges:
        if part == beat_part:
            return random.uniform(range_min, range_max)


def mix_and_save(beat_parts, beat_name, beat_duration):
    #TODO: configure soundfont directory 
    #TODO: levels and pan in a json file
    beat_soundfont = get_random_sound_font(str(os.path.join('sf','beat')))
    print("Beat soundfont: " + beat_soundfont)
    print("Mixing song parts...")    
    beat_part_boards = {}
    beat_part_levels = {}
    beat_part_pan = {}
    
    mix = AudioSegment.silent(duration=beat_duration*1000)
    
    for beat_part in beat_parts:
        beat_part_wav = beat_name + "-" + beat_part + ".wav"
        beat_part_wav = os.path.join(beat_name, beat_part_wav)
        FluidSynth(beat_soundfont).midi_to_audio(beat_parts[beat_part], beat_part_wav)
        board = generate_pedalboard('beat_fx.json')
        beat_part_boards[beat_part] = board
        beat_part_render = AudioSegment.from_wav(apply_fx_to_layer(beat_part_wav, board))
        beat_part_levels[beat_part] = get_beat_part_level(beat_part)
        beat_part_render.volume = float(beat_part_levels[beat_part])
        beat_part_pan[beat_part] = get_beat_part_pan(beat_part)
        beat_part_render.pan(float(beat_part_pan[beat_part]))
        mix = mix.overlay(beat_part_render)

    mix_file = beat_name + '.wav'
    mix_file = os.path.join(beat_name, mix_file) 
    mix.export(mix_file, format='wav')
    print("Beat saved as: " + mix_file)
    return mix_file, beat_soundfont, beat_part_boards, beat_part_levels, beat_part_pan

def create_random_beat(name):
    start_time = time.time()
    tempo = generate_random_tempo()
    time_signature = generate_random_time_signature()
    measures = generate_beat_size()
    beat_elements = generate_beat_elements()
    
    beat_info = {}
    beat_info['name'] = name
    beat_info['tempo'] = tempo
    beat_info['time_signature'] = time_signature
    beat_info['measures'] = measures
    beat_info['elements'] = beat_elements
    
    beat_structure, midi_filenames, duration = generate_beat(tempo, time_signature, measures, name, beat_elements)
    
    beat_info['duration'] = duration    
    beat_info['structure'] = beat_structure
    # beat_info['midi_files'] = midi_filenames

    print("Beat:", beat_structure)
    print("Filenames:", midi_filenames)

    mix_file, beat_soundfont, beat_part_boards, levels, panning = mix_and_save(midi_filenames, name, duration)
    
    beat_info['soundfont'] = beat_soundfont
    
    beat_info['levels'] = levels
    
    beat_info['panning'] = panning
    
    beat_part_boards_js = {}
    
    for part in beat_part_boards:
        beat_part_boards_js[part] = pedalboard_info_json(beat_part_boards[part])    
    
    beat_info['fx'] = beat_part_boards_js
    beat_info['file_name'] = mix_file
    
    json_file = os.path.join(name, name + '.json')
    
    print('Annotations: ' + json_file)
    
    with open(json_file, 'w') as outfile:
        json.dump(beat_info, outfile, indent=4)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.2f} seconds')

        
    return mix_file, json_file



# Example usage

for i in range(100):
    now = datetime.now()
    beat_gen_name = now.strftime("%Y%m%d%H%M%S")
    create_random_beat(beat_gen_name)

