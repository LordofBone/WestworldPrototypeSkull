import logging
import time
from threading import Thread

import numpy as np

from EventHive.event_hive_runner import EventActor
from components.audio_system import audio_engine_access
from config.audio_config import loopback_name, microphone_name
from config.custom_events import MovementEvent, ConversationDoneEvent
from hardware.jaw_controller import JawController

logger = logging.getLogger(__name__)


# Define a generic interface for jaw movement handling
class JawMovementHandler:
    def start_movement(self, event_type=None, event_data=None):
        raise NotImplementedError


# Implement the real jaw movement handling
class RealJawMovementHandler(JawMovementHandler):
    def __init__(self, audio_jaw_sync):
        self.audio_jaw_sync = audio_jaw_sync

    def start_movement(self, event_type=None, event_data=None):
        self.audio_jaw_sync.audio_to_jaw_movement(event_type=None, event_data=event_data)


# Implement the test jaw movement handling
class TestJawMovementHandler(JawMovementHandler):
    def __init__(self, audio_jaw_sync):
        self.audio_jaw_sync = audio_jaw_sync

    def start_movement(self, event_type=None, event_data=None):
        logger.debug("Jaw Audio Test Mode - No actual movement")
        # todo: move this produce event into main class?
        self.audio_jaw_sync.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))

        return True


class AudioJawSync(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        self.servo_controller = JawController()
        self.path = audio_engine_access().path
        audio_engine_access().set_microphone_name(mic_key="USB Microphone", mic_name=microphone_name)
        audio_engine_access().set_microphone_name(mic_key="Loopback", mic_name=loopback_name)
        self.analyzing = False

        self.hw_accel = False

        self.seconds_to_analyze = 30

        self.max_rms = 50  # Set the maximum RMS value to 50
        self.min_rms = 15  # Set the minimum RMS value to 15

        # Normalize RMS value to desired pulse width range (25 to 75)
        self.min_pulse_width = self.servo_controller.close_pulse_width
        self.max_pulse_width = self.servo_controller.open_pulse_width

        self.jaw_movement_handler = TestJawMovementHandler(self) if test_mode else RealJawMovementHandler(self)
        logger.debug("Initialized")

    def set_jaw_position(self, pulse_width, event_type=None, event_data=None):
        self.servo_controller.set_pulse_width(pulse_width)

    def close_jaw(self, event_type=None, event_data=None):
        self.set_jaw_position(self.servo_controller.close_pulse_width)

    def open_jaw(self, event_type=None, event_data=None):
        self.set_jaw_position(self.servo_controller.open_pulse_width)

    def calculate_rms_on_cpu(self):
        self.rms = min(np.sqrt(np.mean(self.data ** 2)), self.max_rms)

    def activate_audio_to_jaw_movement(self, event_type=None, event_data=None):
        logger.debug("Audio to jaw movement")

        Thread(target=self.jaw_movement_handler.start_movement, args=(event_type, event_data,), daemon=True).start()

        return True

    def analyze_audio(self, device="Microphone"):
        audio_engine_access().init_recording_stream(mic_key=device)

        try:
            while self.analyzing:
                start_time = time.time()  # Record the start time

                # Read data
                self.data = np.frombuffer(audio_engine_access().read_recording_stream(mic_key=device),
                                          dtype=np.int16)

                # Calculate RMS
                self.calculate_rms_on_cpu()

                # Check if RMS exceeds the threshold
                if self.rms > self.min_rms:
                    # Normalize RMS value to desired pulse width range
                    normalized_rms = self.rms / self.max_rms
                    pulse_width = (normalized_rms * (
                            self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width

                    logger.debug(f"RMS: {self.rms} | Pulse width: {pulse_width}")

                    # Set pulse width
                    self.set_jaw_position(pulse_width)
                else:
                    logger.debug("RMS below threshold, closing jaw")
                    self.close_jaw()

                # Print processing time
                end_time = time.time()  # Record the end time
                processing_time = end_time - start_time
                logger.debug(f"Processing time: {processing_time:.6f} seconds")
        except Exception as e:
            logger.exception("Exception occurred during audio analysis: " + str(e))
        finally:
            # Always close the stream when we're done to prevent resource leaks
            logger.debug("Audio analysis done, closing jaw and audio stream")
            self.close_jaw()
            audio_engine_access().close_recording_stream(mic_key=device)

            return True

    def audio_to_jaw_movement(self, event_type=None, event_data=None):
        logger.debug("Audio to jaw movement")

        try:
            if event_data is None:
                # Start audio analysis in a separate thread
                audio_analysis_thread = Thread(target=self.analyze_audio, args=("USB Microphone",), daemon=True)
                audio_analysis_thread.start()

                self.analyzing = True
                # Wait for the specified number of seconds
                time.sleep(self.seconds_to_analyze)
                self.analyzing = False
            else:
                # Start audio analysis in a separate thread
                audio_analysis_thread = Thread(target=self.analyze_audio, args=("Loopback",), daemon=True)
                audio_analysis_thread.start()

                self.analyzing = True
                # Set and play audio file from location
                audio_engine_access().audio_file = event_data
                audio_engine_access().play_audio()
                self.analyzing = False
        finally:
            self.analyzing = False
            self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))
            return True

    def get_event_handlers(self):
        return {
            "JAW_TTS_AUDIO": self.activate_audio_to_jaw_movement
        }

    def get_consumable_events(self):
        return [MovementEvent]
