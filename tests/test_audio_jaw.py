import logging

from EventHive.event_hive_runner import EventQueue
from components.jaw_system import AudioJawSync
from config.custom_events import MovementEvent

# Configure logging level
logging.basicConfig(level=logging.DEBUG)


class AudioJawSyncTest:
    def __init__(self):
        # Create an instance of the class and start it
        self.event_queue = EventQueue()
        jaw_system_test = AudioJawSync(self.event_queue)
        jaw_system_test.start()

    def test_audiofile_to_jaw(self):
        event = MovementEvent(["JAW_TEST_AUDIO"], 1)
        self.event_queue.queue_addition(event)

    def test_mic_to_jaw(self, seconds_to_analyze=30):
        event = MovementEvent([f"JAW_TTS_AUDIO"], 1)
        self.event_queue.queue_addition(event)
