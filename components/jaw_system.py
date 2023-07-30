import logging
import time
from threading import Thread

import numpy as np
import pyaudio

from EventHive.event_hive_runner import EventActor
from components.audio_system import AudioEngineAccess
from config.custom_events import MovementEvent, MicrowaveControllerEvent
from hardware.jaw_controller import JawController

logger = logging.getLogger(__name__)


class AudioJawSync(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        self.p = pyaudio.PyAudio()
        self.input_device = int(self.find_usb_microphone_device())

        self.servo_controller = JawController()

        self.path = AudioEngineAccess.path

        self.analyzing = False

        self.rms = None
        self.data = None

        self.hw_accel = False

        self.seconds_to_analyze = 30

        # Audio settings
        self.sample_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 384000]
        self.chunk_sizes = [128, 256, 512, 1024, 2048]
        self.RATE = self.find_compatible_sample_rate()  # Find lowest compatible sample rate
        self.CHUNK = self.find_compatible_chunk_size()  # Reduced chunk size
        self.max_rms = 50  # Set the maximum RMS value to 50
        self.min_rms = 15  # Set the minimum RMS value to 15

        # Normalize RMS value to desired pulse width range (25 to 75)
        self.min_pulse_width = self.servo_controller.close_pulse_width
        self.max_pulse_width = self.servo_controller.open_pulse_width

    def find_usb_microphone_device(self):
        # List all audio devices
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            logging.debug(f"Device index: {info['index']} - {info['name']}")

            # Check if the device name contains "USB PnP Sound Device"
            if "USB PnP Sound Device" in info['name']:
                logging.debug("Found USB PnP Sound Device at index:", info['index'])
                return info['index']

        # If the device was not found
        logging.debug("USB PnP Sound Device not found")
        raise Exception("USB PnP Sound Device not found, please ensure it is plugged in.")

    def find_compatible_sample_rate(self):
        # Check for supported sample rates
        for rate in self.sample_rates:
            try:
                is_supported = self.p.is_format_supported(rate,
                                                          input_device=self.input_device,
                                                          input_channels=1,
                                                          input_format=pyaudio.paInt16)
                logging.debug(f"  Sample rate {rate} is supported: {is_supported}")
                return rate
            except ValueError as err:
                logging.debug(f"  Sample rate {rate} is NOT supported: {err}")

    # Check for supported chunk sizes
    def find_compatible_chunk_size(self):
        for chunk_size in self.chunk_sizes:
            try:
                # Attempt to open a stream with the given chunk size
                # If this fails, it will throw an exception which is caught in the except block
                stream = self.p.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=self.RATE,  # Use the rate determined previously
                                     input=True,
                                     frames_per_buffer=chunk_size,
                                     input_device_index=self.input_device)

                # If we reach this line, the chunk size is supported. Close the stream and return the chunk size.
                stream.close()
                logging.debug(f"  Chunk size {chunk_size} is supported.")
                return chunk_size
            except Exception as err:
                # This chunk size is not supported. Continue checking the next one.
                logging.debug(f"  Chunk size {chunk_size} is NOT supported: {err}")

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
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK,
                             input_device_index=self.input_device)

        try:
            while self.analyzing:
                start_time = time.time()  # Record the start time

                # Read data
                self.data = np.frombuffer(stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.int16)

                # Calculate RMS
                self.calculate_rms_on_cpu()

                # Check if RMS exceeds the threshold
                if self.rms > self.min_rms:
                    # Normalize RMS value to desired pulse width range
                    normalized_rms = self.rms / self.max_rms
                    pulse_width = (normalized_rms * (
                                self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width

                    logging.debug(f"RMS: {self.rms} | Pulse width: {pulse_width}")

                    # Set pulse width
                    self.set_jaw_position(pulse_width)
                else:
                    logging.debug("RMS below threshold, closing jaw")
                    self.close_jaw()

                # Print processing time
                end_time = time.time()  # Record the end time
                processing_time = end_time - start_time
                logging.debug(f"Processing time: {processing_time:.6f} seconds")
        finally:
            # Always close the stream when we're done to prevent resource leaks
            logging.debug("Audio analysis done, closing jaw and audio stream")
            self.close_jaw()
            stream.close()

            return True

        # logging.debug("Audio, closing jaw")
        # self.close_jaw()

    def audio_to_jaw_movement(self, event_type=None, event_data=None):
        logging.debug("Audio to jaw movement")
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
                AudioEngineAccess.audio_file = event_data
                AudioEngineAccess.play_audio()

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
