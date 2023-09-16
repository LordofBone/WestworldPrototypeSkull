import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from time import sleep
from config.audio_config import microphone_name
from Lakul.integrate_stt import SpeechtoTextHandler


def test_real_hardware_stt():
    # Initialize STT handler
    SpeechtoText = SpeechtoTextHandler(microphone_name)
    SpeechtoText.model_size = "tiny"

    # Prompt the user
    expected_phrase = "Testing Whisper speech to text"
    print(f"Please say the following phrase clearly, after the countdown: '{expected_phrase}'")

    # Countdown
    for i in range(5, 0, -1):
        print(i)
        sleep(1)
    print("SPEAK!")

    # Record and transcribe
    SpeechtoText.initiate_recording()
    print("Inferencing...")
    transcription = SpeechtoText.run_inference()

    # Display transcription
    print(f"Transcription: {transcription}")

    # Assertions
    if not transcription:
        print("Test failed: The transcription result is empty.")
        return
    if "Testing" not in transcription and "Whisper" not in transcription:
        print("Test failed: The transcription does not match the expected phrase.")
        return

    print("Test completed. Please verify the transcription for accuracy.")
    print("All tests passed.")


if __name__ == "__main__":
    # Run the real hardware test
    test_real_hardware_stt()
