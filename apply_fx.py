import random
from pedalboard import Pedalboard, Compressor, Gain, Chorus, LadderFilter, Phaser, Delay, Reverb
from pedalboard.io import AudioFile
import json

# Load effect parameters from the JSON file
with open('effects.json', 'r') as json_file:
    effect_parameters = json.load(json_file)

def apply_fx_to_layer(wav_file, effect_params):
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
    board = Pedalboard([create_effect(effect_class, parameters)
                        for effect_class, parameters in effects])

    # Apply the effects to the input file        
    with AudioFile(wav_file) as af:
        with AudioFile(wav_file+'_fx.wav', 'w', af.samplerate, af.num_channels) as of:        
            while af.tell() < af.frames:
                chunk = af.read(af.samplerate)
                effected = board(chunk, af.samplerate, reset=False)
                of.write(effected)
              
    return wav_file+'_fx.wav'

# Generate random values for the effect parameters based on probability and value range
def create_effect(effect_class, parameters):
    # Unpack the parameters
    probability = parameters['probability']
    value_range = parameters['value_range']
    
    if random.random() < probability:
        kwargs = {param: random.uniform(value_range[param][0], value_range[param][1])
                  for param in value_range}
        return effect_class(**kwargs)
    return None

# Example usage with effect parameters with probability and value range

input_file = 'input.wav'

output_file = apply_fx_to_layer('input.wav', effect_parameters)
print("Output file:", output_file)
