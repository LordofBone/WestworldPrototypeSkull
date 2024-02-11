from pathlib import Path

profanity_censor_enabled = True

file_name = "stt_recording.wav"

stt_audio_path = Path(__file__).parent.parent / 'audio' / file_name

offline_mode = True

# available_models = ["tiny", "base", "small", "medium", "large"]
model_size = "tiny"

# max amount of seconds to record audio for STT
recording_max_seconds = 60

# silence duration until recording for STT stops, in seconds
recording_silence_duration = 3

# silence threshold for STT recording
recording_silence_threshold = 40
