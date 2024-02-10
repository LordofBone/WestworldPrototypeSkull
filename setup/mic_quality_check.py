import sys

from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from components.audio_system import audio_engine_access

from config.audio_config import microphone_name
from Lakul.integrate_stt import SpeechtoTextHandler


def main():
    audio_engine_access().audio_file = Path(__file__).parent.parent / 'Lakul' / 'audio' / 'recording.wav'

    # Initialize STT handler
    SpeechtoText = SpeechtoTextHandler(stt_microphone_name=microphone_name, init_on_launch=False)

    # Record and transcribe
    print("Recording...")
    SpeechtoText.initiate_recording(max_seconds=20, silence_duration=2, silence_threshold=1000)
    print("Finished recording")

    # Set and play audio file from location
    print("Playing audio...")
    audio_engine_access().play_audio()
    print("Done playing audio")


if __name__ == "__main__":
    # Run the test
    main()
