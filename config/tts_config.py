import os
import sys
from pathlib import Path

# Options are: pyttsx3/fakeyou/nix
tts_mode = "nix"

pyttsx3_voice = 2

nix_dir = os.path.join(Path(__file__).parent.parent, 'nix-tts')
audio_dir = Path(__file__).parent.parent / f"audio"

determ_model_path = Path(__file__).parent.parent / f"models/deterministic"
stoch_model_path = Path(__file__).parent.parent / f"models/stochastic"

boot_text = "Welcome to the Arasaka Relic Cyberware System; Trauma Team Edition"
boot_text_test = "Welcome to the Arasaka Relic Cyberware System; Trauma Team Edition. Testing mode active."

reboot_text = "Rebooting the system, please wait."
shutdown_text = "Shutting down the system, please wait."
demo_text = "Hello, my name is Skull. I am a conversational AI. I am a demo version of the full Skull AI."

audio_on = True
file_name = "tts_output.wav"

# nix_dir = Path(__file__).parent.parent / 'nix-tts'

jaw_test_audio_path = Path(__file__).parent.parent / 'audio' / 'jaw_test.wav'

whisper_test_audio_path = Path(__file__).parent.parent / 'audio' / 'whisper_test.wav'

tts_audio_path = Path(__file__).parent.parent / 'audio' / 'tts_output.wav'

sys.path.append(str(jaw_test_audio_path))

sys.path.append(str(whisper_test_audio_path))

sys.path.append(str(tts_audio_path))
