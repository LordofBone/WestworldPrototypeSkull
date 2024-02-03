import logging
import threading
from time import sleep

import numpy as np

from EventHive.event_hive_runner import EventActor
from components.audio_system import audio_engine_access
from config.audio_config import audio_input_detection_threshold
from config.custom_events import DetectEvent, AudioDetectControllerEvent, ConversationDoneEvent

logger = logging.getLogger(__name__)


# Define a generic audio detection handler interface
class AudioDetectionHandler:
    def start_scan(self):
        raise NotImplementedError

    def stop_scan(self):
        raise NotImplementedError


# Implement the real audio detection handler
class RealAudioDetectionHandler(AudioDetectionHandler):
    def __init__(self, audio_detector):
        self.audio_detector = audio_detector

    def start_scan(self):
        audio_engine_access().init_recording_stream(mic_key=self.audio_detector.mic_key)

    def stop_scan(self):
        audio_engine_access().close_recording_stream(mic_key=self.audio_detector.mic_key)

    def audio_scan(self):
        logger.debug(f"Audio scan enabled with detection threshold: {audio_input_detection_threshold}")

        while True:
            if self.audio_detector.scan_mode_enabled:
                sleep(1)
                audio_data = audio_engine_access().read_recording_stream(self.audio_detector.mic_key)
                audio_amplitude = np.frombuffer(audio_data, dtype=np.int16)
                if np.max(audio_amplitude) > audio_input_detection_threshold:
                    self.audio_detector.produce_event(DetectEvent(["HUMAN_DETECTED"], 1))
                    logger.debug(
                        f"Sound detected with amplitude {np.max(audio_amplitude)} exceeding threshold "
                        f"{audio_input_detection_threshold}")
                    self.audio_detector.scan_mode_off()


# Implement the test audio detection handler
class TestAudioDetectionHandler(AudioDetectionHandler):
    def __init__(self, audio_detector):
        self.audio_detector = audio_detector

    def start_scan(self):
        pass  # No operation for test mode start scan

    def stop_scan(self):
        pass  # No operation for test mode stop scan

    def audio_scan(self):
        logger.debug("Audio scan test thread enabled")

        while True:
            if self.audio_detector.scan_mode_enabled:
                # todo: figure out why sleep is required here, without it conversation engine stalls
                sleep(1)
                self.audio_detector.produce_event(DetectEvent(["HUMAN_DETECTED"], 1))
                logger.debug(f"Simulation of sound detected for test mode.")
                self.audio_detector.scan_mode_off()


class AudioDetector(EventActor):
    def __init__(self, event_queue, test_mode=False):
        super().__init__(event_queue)
        self.scan_mode_enabled = False
        self.scan_thread = None
        self.path = audio_engine_access().path
        self.mic_key = "DETECTION_MIC"
        audio_engine_access().set_microphone_name(self.mic_key, "USB PnP Sound Device")

        # Initialize the appropriate handler based on test_mode
        self.audio_detection_handler = TestAudioDetectionHandler(self) if test_mode else RealAudioDetectionHandler(self)

        logger.debug("Initialized")

    def scan_mode_on(self, event_type=None, event_data=None):
        self.audio_detection_handler.start_scan()
        self.scan_mode_enabled = True
        if not self.scan_thread:
            self.scan_thread = threading.Thread(target=self.audio_detection_handler.audio_scan, daemon=True)
            self.scan_thread.start()
            logger.debug(f"Scan mode on, mic opened, thread started: {self.scan_thread}")
        else:
            self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))
            logger.debug(f"Audio already setup, thread already started: {self.scan_thread}, so just producing event "
                         f"to move to next conversation action")

        return True

    def scan_mode_off(self, event_type=None, event_data=None):
        self.scan_mode_enabled = False
        if self.scan_thread:
            self.audio_detection_handler.stop_scan()
            logger.debug("Scan mode off, mic closed")

        return True

    def get_event_handlers(self):
        return {
            "SCAN_MODE_ON": self.scan_mode_on,
            "SCAN_MODE_OFF": self.scan_mode_off
        }

    def get_consumable_events(self):
        return [AudioDetectControllerEvent]
