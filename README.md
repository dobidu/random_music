# random_music 
## Python Random (but 'coherent') Music Generator

This project uses Python to generate music in various formats such as MIDI, audio, and sheet music. It makes use of the following libraries:

- `midiutil` - for creating MIDI files
- `music21` - for working with sheet music
- `pydub` - for working with audio files
- `midi2audio` - for converting MIDI files to audio using a SoundFont synthesizer
- `pedalboard` - for audio effects
- `random` - for generating random music sequences
- `os` - for working with file paths and directories
- `time` - for time measuring
- `json` - for JSON handling

## Installation
1. Clone this repository:
```bash
git clone https://github.com/dobidu/random_music/
```

2. Install the required dependencies:
```bash
pip install midiutil music21 pydub midi2audio pedalboard
```

3. Install FluidSynth synthesizer (required for converting MIDI to audio):

### on OS X
```bash
brew install fluidsynth
```

### on Debian/Ubuntu 
```bash
sudo apt-get install fluidsynth
```

4. See the example usage in random_song.py; run it using:
```bash
python3 random_song.py
```
