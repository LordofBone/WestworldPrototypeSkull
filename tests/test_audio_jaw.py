import logging
import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

import utils.logging_system
from EventHive.event_hive_runner import EventQueue
from components.jaw_system import AudioJawSync
from config.custom_events import MovementEvent
from config.tts_config import tts_audio_path

# Configure logging level
logging.basicConfig(level=logging.DEBUG)


class AudioJawSyncTest:
    def __init__(self):
        # Create an instance of the class and start it
        self.event_queue = EventQueue()
        jaw_system_test = AudioJawSync(self.event_queue)
        jaw_system_test.start()

    def test_audiofile_to_jaw(self):
        logging.debug("Testing audiofile to jaw")
        event = MovementEvent(["JAW_TTS_AUDIO", tts_audio_path], 1)
        self.event_queue.queue_addition(event)

    def test_mic_to_jaw(self, seconds_to_analyze=30):
        logging.debug("Testing mic to jaw")
        event = MovementEvent(["JAW_TTS_AUDIO"], 1)
        self.event_queue.queue_addition(event)


audio_jaw_sync_test = AudioJawSyncTest()
audio_jaw_sync_test.seconds_to_analyze = 120

audio_jaw_sync_test.test_audiofile_to_jaw()
audio_jaw_sync_test.test_mic_to_jaw()
