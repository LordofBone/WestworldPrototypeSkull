import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

import utils.logging_system
from EventHive.event_hive_runner import EventQueue
from components.jaw_system import AudioJawSync
from config.custom_events import MovementEvent
from config.tts_config import jaw_test_audio_path
import unittest
import logging
import threading
from time import sleep


class EnhancedAudioJawSyncTest(unittest.TestCase):

    def setUp(self):
        """Setup method to initialize necessary components before each test."""
        self.event_queue = EventQueue()
        self.audio_jaw_sync = AudioJawSync(self.event_queue)
        self.audio_jaw_sync.start()

    def tearDown(self):
        """Teardown method to free resources after each test."""
        self.audio_jaw_sync.analyzing = False

        # If there's any active threads, join them (stop them)
        for thread in threading.enumerate():
            if thread.is_alive():
                try:
                    thread.join(1)  # Give the thread 1 second to finish
                except Exception as e:
                    logging.error(f"Error stopping thread: {e}")

        # If there's any other cleanup specific to your application, add them here

        # Ensure proper shutdown of the EventActor thread
        self.audio_jaw_sync.shutdown()


class TestExistingMethods(EnhancedAudioJawSyncTest):

    def test_audiofile_to_jaw(self):
        logging.debug("Testing audiofile to jaw")
        event = MovementEvent(["JAW_TTS_AUDIO", jaw_test_audio_path], 1)
        self.event_queue.queue_addition(event)
        sleep(5)  # Give some time for the audio to play and be analyzed
        while self.audio_jaw_sync.analyzing:
            pass
        logging.debug("Done testing audiofile to jaw")

    def test_mic_to_jaw(self):
        logging.debug("Testing mic to jaw")
        event = MovementEvent(["JAW_TTS_AUDIO"], 1)
        self.event_queue.queue_addition(event)
        sleep(5)  # Give some time for the mic audio to be analyzed
        while self.audio_jaw_sync.analyzing:
            pass
        logging.debug("Done testing mic to jaw")


if __name__ == '__main__':
    unittest.main(verbosity=2)
    print("Active threads:", threading.enumerate())
    sys.exit(0)  # Exit the script
