import sys
import librosa
import numpy as np
from scipy.stats import entropy

if __name__ == '__main__':
    if len(sys.argv) < 2:
      print('Usage: python musicality_measure.py <audio_file>')
      sys.exit(1)
    
    filename=sys.argv[1]

# Define weights for each feature
tempo_weight = 0.05
spectral_contrast_weight = 0.05
chroma_feature_weight = 0.2
tonnetz_feature_weight = 0.05
zero_crossing_rate_weight = 0.02
mfcc_weight = 0.3
spectral_centroid_weight = 0.1
spectral_rolloff_weight = 0.1
rms_weight = 0.05
beat_sync_features_weight = 0.1
audio_length_weight = 0.1
entropy_weight = 0.1

try:
    # Load the audio file
    y, sr = librosa.load(filename)

    # Calculate the Tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Calculate the Spectral Contrast
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    # Calculate the Chroma Feature
    chroma_feature = librosa.feature.chroma_stft(y=y, sr=sr)

    # Calculate the Tonnetz Feature
    tonnetz_feature = librosa.feature.tonnetz(y=y, sr=sr)

    # Calculate the Zero Crossing Rate
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)

    # Calculate the MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr)

    # Calculate the Spectral Centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

    # Calculate the Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

    # Calculate the RMS Energy
    rms = librosa.feature.rms(y=y)

    # Calculate the Beat Sync Features
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_sync_features = librosa.util.sync(y, beats)

    # Normalize the features
    tempo = (tempo - 40) / (240 - 40)
    tempo = 1 - abs(tempo - 0.5)

    spectral_contrast = (spectral_contrast - np.min(spectral_contrast)) / (np.max(spectral_contrast) - np.min(spectral_contrast))
    chroma_feature = (chroma_feature - np.min(chroma_feature)) / (np.max(chroma_feature) - np.min(chroma_feature))
    tonnetz_feature = (tonnetz_feature - np.min(tonnetz_feature)) / (np.max(tonnetz_feature) - np.min(tonnetz_feature))
    zero_crossing_rate = (zero_crossing_rate - np.min(zero_crossing_rate)) / (np.max(zero_crossing_rate) - np.min(zero_crossing_rate))
    mfcc = (mfcc - np.min(mfcc)) / (np.max(mfcc) - np.min(mfcc))
    spectral_centroid = (spectral_centroid - np.min(spectral_centroid)) / (np.max(spectral_centroid) - np.min(spectral_centroid))
    spectral_rolloff = (spectral_rolloff - np.min(spectral_rolloff)) / (np.max(spectral_rolloff) - np.min(spectral_rolloff))
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms))
    beat_sync_features = (beat_sync_features - np.min(beat_sync_features)) / (np.max(beat_sync_features) - np.min(beat_sync_features))

    # Calculate audio length factor
    audio_length = librosa.get_duration(y=y, sr=sr)
    audio_length_factor = 1.0 if audio_length >= 30 else audio_length / 30

    # Calculate probability distribution and entropy
    prob_distribution = np.abs(y) / np.sum(np.abs(y))
    entropy_value = entropy(prob_distribution)

    # Check for white noise
    is_white_noise = entropy_value > 8.0

    # Calculate the musicality based on the extracted features and their weights
    musicality = (
        np.mean(tempo) * tempo_weight +
        np.mean(spectral_contrast) * spectral_contrast_weight +
        np.mean(chroma_feature) * chroma_feature_weight +
        np.mean(tonnetz_feature) * tonnetz_feature_weight +
        np.mean(zero_crossing_rate) * zero_crossing_rate_weight +
        np.mean(mfcc) * mfcc_weight +
        np.mean(spectral_centroid) * spectral_centroid_weight +
        np.mean(spectral_rolloff) * spectral_rolloff_weight +
        np.mean(rms) * rms_weight +
        np.mean(beat_sync_features) * beat_sync_features_weight +
        audio_length_factor * audio_length_weight -
        entropy_value * entropy_weight -
        (0.5 if is_white_noise else 0.0)
    )
    
    # Normalize the musicality value
    musicality_value = (musicality * -1)
    musicality_value = musicality_value - 1

    print('Measuring musicality for audio file: {}\n'.format(filename))

    # Print the parameters and their weights
    print('Tempo: {:.2f} (weight: {:.2f})'.format(np.mean(tempo), tempo_weight))
    print('Spectral Contrast: {:.2f} (weight: {:.2f})'.format(np.mean(spectral_contrast), spectral_contrast_weight))
    print('Chroma Feature: {:.2f} (weight: {:.2f})'.format(np.mean(chroma_feature), chroma_feature_weight))
    print('Tonnetz Feature: {:.2f} (weight: {:.2f})'.format(np.mean(tonnetz_feature), tonnetz_feature_weight))
    print('Zero Crossing Rate: {:.2f} (weight: {:.2f})'.format(np.mean(zero_crossing_rate), zero_crossing_rate_weight))
    print('MFCCs: {:.2f} (weight: {:.2f})'.format(np.mean(mfcc), mfcc_weight))
    print('Spectral Centroid: {:.2f} (weight: {:.2f})'.format(np.mean(spectral_centroid), spectral_centroid_weight))
    print('Spectral Rolloff: {:.2f} (weight: {:.2f})'.format(np.mean(spectral_rolloff), spectral_rolloff_weight))
    print('RMS Energy: {:.2f} (weight: {:.2f})'.format(np.mean(rms), rms_weight))
    print('Beat Sync Features: {:.2f} (weight: {:.2f})'.format(np.mean(beat_sync_features), beat_sync_features_weight))
    print('Audio Length: {:.2f} (weight: {:.2f})'.format(audio_length_factor, audio_length_weight))
    print('Entropy: {:.2f} (weight: {:.2f})'.format(entropy_value, entropy_weight))
    # Print the musicality value
    print('\nEstimated musicality: {:.2f}'.format(musicality_value))

except Exception as e:
    print(f'Error processing audio file: {e}')
