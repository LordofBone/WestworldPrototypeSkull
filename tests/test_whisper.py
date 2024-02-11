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
        self.SpeechtoText_Online = SpeechtoTextHandler(stt_microphone_name=loopback_name, init_on_launch=False,
                                                       stt_offline_mode=False, custom_name="Online STT")
        self.SpeechtoText_Offline = SpeechtoTextHandler(stt_microphone_name=loopback_name, init_on_launch=False,
                                                        stt_offline_mode=True, custom_name="Offline STT")

        self.SpeechtoText_Offline.model_size = "tiny"

        self.SpeechtoText_Offline.init_models()
        self.SpeechtoText_Online.init_models()

    def play_audio(self):
        # Set and play audio file from location
        print(f"Playing audio from: {self.stt_runner.custom_name}...")
        audio_engine_access().play_audio()
        print(f"Done playing audio from {self.stt_runner.custom_name}...")

    def record_and_transcribe(self):
        # Record and transcribe
        print(f"Recording with {self.stt_runner.custom_name}...")
        self.stt_runner.initiate_recording(max_seconds=20, silence_duration=20, silence_threshold=1000)
        print(f"Finished recording with {self.stt_runner.custom_name}...")
        print(f"Inferencing with {self.stt_runner.custom_name}...")
        transcription = self.stt_runner.run_inference()
        self.transcription_queue.put(transcription)
        print(f"Finished inferencing with {self.stt_runner.custom_name}...")

    def test_real_hardware_stt(self):
        # todo: look into making this record the master audio file then play it out again to be analysed by STT? this
        #  would test STT and mic quality automatically; but had some issues implementing before with no audio being
        #  recorded, could be a loopback/mic being activated same time issue?
        for mode in ('Online', 'Offline'):
            with self.subTest(mode=mode):
                if mode == 'Online':
                    self.stt_runner = self.SpeechtoText_Online
                else:
                    self.stt_runner = self.SpeechtoText_Offline

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

                # Assertions and checks
                self.assertTrue(transcription, "The transcription result is empty.")
                self.assertIn("testing", transcription.lower(),
                              "The transcription does not match the expected phrase 'Testing'.")
                self.assertIn("whisper", transcription.lower(),
                              "The transcription does not match the expected phrase 'Whisper'.")

                print(f"Test completed for {mode} mode. Please verify the transcription for accuracy.")


if __name__ == "__main__":
    # Run the test
    unittest.main(verbosity=2)
