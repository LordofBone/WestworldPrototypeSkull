from pathlib import Path

profanity_censor_enabled = True

file_name = "stt_recording.wav"

stt_audio_path = Path(__file__).parent.parent / 'audio' / file_name

offline_mode = True

# available_models = ["tiny", "base", "small", "medium", "large"]
model_size = "tiny"
