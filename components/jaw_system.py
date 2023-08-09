import logging
import time
from threading import Thread

import numpy as np

from EventHive.event_hive_runner import EventActor
from components.audio_system import audio_engine_access
from config.custom_events import MovementEvent, MicrowaveControllerEvent
from hardware.jaw_controller import JawController

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class AudioJawSync(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        self.servo_controller = JawController()

        self.path = audio_engine_access().path
        audio_engine_access().set_microphone_name("Loopback: PCM (hw:2,1)")

        self.analyzing = False

        self.rms = None
        self.data = None

        self.hw_accel = False

        self.seconds_to_analyze = 30

        self.max_rms = 50  # Set the maximum RMS value to 50
        self.min_rms = 15  # Set the minimum RMS value to 15

        # Normalize RMS value to desired pulse width range (25 to 75)
        self.min_pulse_width = self.servo_controller.close_pulse_width
        self.max_pulse_width = self.servo_controller.open_pulse_width

    def set_jaw_position(self, pulse_width, event_type=None, event_data=None):
        self.servo_controller.set_pulse_width(pulse_width)

    def close_jaw(self, event_type=None, event_data=None):
        self.set_jaw_position(self.min_pulse_width)

    def open_jaw(self, event_type=None, event_data=None):
        self.set_jaw_position(self.max_pulse_width)

    def calculate_rms_on_cpu(self):
        # Calculate RMS and clip to max RMS
        self.rms = min(np.sqrt(np.mean(self.data ** 2)), self.max_rms)

    def analyze_audio(self):
        audio_engine_access().init_recording_stream()

        try:
            while self.analyzing:
                start_time = time.time()  # Record the start time

                # Read data
                self.data = np.frombuffer(audio_engine_access().read_recording_stream(), dtype=np.int16)

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
            audio_engine_access().close_recording_stream()

            return True

    def audio_to_jaw_movement(self, event_type=None, event_data=None):
        logger.debug("Audio to jaw movement")
        # Start audio analysis in a separate thread
        audio_analysis_thread = Thread(target=self.analyze_audio)
        audio_analysis_thread.daemon = False  # Daemon thread will exit when the main program exits
        audio_analysis_thread.start()

        try:

            if event_data is None:
                self.analyzing = True

                # Wait for the specified number of seconds
                time.sleep(self.seconds_to_analyze)

                # Stop analyzing when time has elapsed
                self.analyzing = False
            else:
                self.analyzing = True

                # Set and play audio file from location
                audio_engine_access().audio_file = event_data
                audio_engine_access().play_audio()

                # Stop analyzing when audio is done playing
                self.analyzing = False

        finally:

            # Stop analyzing when audio is done playing
            self.analyzing = False

            self.produce_event(MicrowaveControllerEvent(["SCAN_MODE_ON"], 1))

            return True

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers that this consumer can handle.
        :return:
        """
        return {
            "JAW_TTS_AUDIO": self.audio_to_jaw_movement
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [MovementEvent]
