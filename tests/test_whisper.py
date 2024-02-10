import queue
import sys
import threading
import unittest
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from components.audio_system import audio_engine_access

from config.audio_config import loopback_name
from config.tts_config import whisper_test_audio_path
from Lakul.integrate_stt import SpeechtoTextHandler


class TestWhisperSTT(unittest.TestCase):
    def setUp(self):
        self.path = audio_engine_access().path
        audio_engine_access().audio_file = whisper_test_audio_path
        self.transcription_queue = queue.Queue()

        # Initialize STT handler with loopback
        self.SpeechtoText = SpeechtoTextHandler(stt_microphone_name=loopback_name, init_on_launch=False)
        self.SpeechtoText.model_size = "tiny"
        self.SpeechtoText.init_models()

    def play_audio(self):
        # Set and play audio file from location
        audio_engine_access().play_audio()
        print("Done playing audio")

    def record_and_transcribe(self):
        # Record and transcribe
        print("Recording...")
        self.SpeechtoText.initiate_recording(max_seconds=20, silence_duration=2, silence_threshold=1000)
        print("Inferencing...")
        transcription = self.SpeechtoText.run_inference()
        self.transcription_queue.put(transcription)

    def test_real_hardware_stt(self):
        # Create threads for audio and transcription
        audio_thread = threading.Thread(target=self.play_audio)

        transcription_thread = threading.Thread(target=self.record_and_transcribe)

        # Start threads
        audio_thread.start()
        transcription_thread.start()

        # Wait for threads to finish
        audio_thread.join()
        transcription_thread.join()

        # Retrieve the transcription from the queue
        transcription = self.transcription_queue.get()

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
    # Run the test
    unittest.main(verbosity=2)
