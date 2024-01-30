import logging
import threading

import numpy as np

from EventHive.event_hive_runner import EventActor
from components.audio_system import audio_engine_access
from config.audio_config import audio_input_detection_threshold
from config.custom_events import DetectEvent, AudioDetectControllerEvent, TTSDoneEvent

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class AudioDetector(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)
        self.scan_mode_enabled = False
        self.path = audio_engine_access().path
        self.mic_key = "DETECTION_MIC"
        audio_engine_access().set_microphone_name(self.mic_key, "USB PnP Sound Device")
        self.scan_thread = None
        logger.debug(f"Audio detection threshold: {audio_input_detection_threshold}")

    def audio_scan(self):
        while True:
            if self.scan_mode_enabled:
                audio_data = audio_engine_access().read_recording_stream(self.mic_key)
                audio_amplitude = np.frombuffer(audio_data, dtype=np.int16)
                # Check if amplitude exceeds a threshold
                if np.max(audio_amplitude) > audio_input_detection_threshold:
                    self.produce_event(DetectEvent(["HUMAN_DETECTED"], 1))
                    logger.debug(
                        f"Sound detected with amplitude {np.max(audio_amplitude)} exceeding threshold {audio_input_detection_threshold}")
                    self.scan_mode_off()

    def scan_mode_on(self, event_type=None, event_data=None):
        logger.debug("SCAN MODE ON")
        # Spawn a new thread to run the audio scan function
        if not self.scan_thread:
            self.scan_thread = threading.Thread(target=self.audio_scan, daemon=True)
            self.scan_thread.start()
        else:
            self.produce_event(TTSDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))

        audio_engine_access().init_recording_stream(mic_key=self.mic_key)
        self.scan_mode_enabled = True
        return True

    def scan_mode_off(self, event_type=None, event_data=None):
        logger.debug("SCAN MODE OFF")
        audio_engine_access().close_recording_stream(mic_key=self.mic_key)
        self.scan_mode_enabled = False
        return True

    def get_event_handlers(self):
        return {
            "SCAN_MODE_ON": self.scan_mode_on,
            "SCAN_MODE_OFF": self.scan_mode_off,
        }

    def get_consumable_events(self):
        return [AudioDetectControllerEvent]
