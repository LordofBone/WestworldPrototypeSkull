import sys
from pathlib import Path

nix_dir = Path(__file__).parent.parent / 'nix-tts'

test_audio_path = Path(__file__).parent.parent / 'audio' / 'test.wav'

tts_audio_path = Path(__file__).parent.parent / 'audio' / 'tts_output.wav'

sys.path.append(str(test_audio_path))

sys.path.append(str(tts_audio_path))
