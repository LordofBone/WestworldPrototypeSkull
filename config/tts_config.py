import os
import sys
from pathlib import Path

# Options are: pyttsx3/fakeyou/nix/openai
tts_mode = "nix"

# Options are tts-1, tts-1-hd
openai_model = "tts-1"

# Options are: alloy/echo/fable/onyx/nova/shimmer
openai_voice = "onyx"

pyttsx3_voice = 2

nix_dir = os.path.join(Path(__file__).parent.parent, 'nix-tts')
audio_dir = Path(__file__).parent.parent / f"audio"

determ_model_path = Path(__file__).parent.parent / f"models/deterministic"
stoch_model_path = Path(__file__).parent.parent / f"models/stochastic"

boot_text = "Welcome to the Westworld Prototype Host System, awaiting configuration."
boot_text_test = "Welcome to the Westworld Prototype Host System. Testing mode active."

reboot_text = "Rebooting the system, please wait."
shutdown_text = "Shutting down the system, please wait."
demo_text = ("Hello, I am a Westworld Prototype Host. This is a demo of my conversational abilities. I am a prototype "
             "host, awaiting configuration.")
greeting_text = "Hello"
override_text = "Override command detected. Activating command system."
test_text = "Test command detected. Command system working."
test_command_text = "Test command detected. Command system working."
no_command_text = "I'm sorry, I didn't understand that command."

audio_on = True
file_name = "tts_output.wav"

jaw_test_audio_path = Path(__file__).parent.parent / 'audio' / 'jaw_test.wav'

whisper_test_audio_path = Path(__file__).parent.parent / 'audio' / 'whisper_test.wav'

tts_audio_path = Path(__file__).parent.parent / 'audio' / file_name

sys.path.append(str(jaw_test_audio_path))

sys.path.append(str(whisper_test_audio_path))

sys.path.append(str(tts_audio_path))
