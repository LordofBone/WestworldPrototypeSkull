import sys
from pathlib import Path

nix_dir = Path(__file__).parent.parent / 'nix-tts'

test_audio_path = Path(__file__).parent.parent / 'audio' / 'test.wav'

tts_audio_path = Path(__file__).parent.parent / 'audio' / 'tts_output.wav'

chatting_gpt_dir = Path(__file__).parent.parent / 'ChattingGPT'


def setup_paths():
    sys.path.append(str(nix_dir))

    sys.path.append(str(test_audio_path))

    sys.path.append(str(tts_audio_path))

    sys.path.append(str(chatting_gpt_dir))
