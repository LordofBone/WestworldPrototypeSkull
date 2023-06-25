import logging
import time
from threading import Thread

import numpy as np
import pyaudio
from playsound import playsound

from hardware.jaw_controller import JawController


def play_audio(audio_file):
    playsound(audio_file)


class AudioJawSync:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_device = int(self.find_usb_microphone_device())

        self.servo_controller = JawController()

        self.analyzing = False

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

    def analyze_audio(self):
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK,
                             input_device_index=self.input_device)

        while self.analyzing:
            start_time = time.time()  # Record the start time

            # Read data
            data = np.frombuffer(stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.int16)

            # Calculate RMS and clip to max RMS
            rms = min(np.sqrt(np.mean(data ** 2)), self.max_rms)

            # Check if RMS exceeds the threshold
            if rms > self.min_rms:
                # Normalize RMS value to desired pulse width range
                normalized_rms = rms / self.max_rms
                pulse_width = (normalized_rms * (self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width

                logging.debug(f"RMS: {rms} | Pulse width: {pulse_width}")

                # Set pulse width
                self.servo_controller.set_pulse_width(pulse_width)
            else:
                logging.debug("RMS below threshold, closing jaw")
                self.servo_controller.set_pulse_width(self.min_pulse_width)

            # Print processing time
            end_time = time.time()  # Record the end time
            processing_time = end_time - start_time
            logging.debug(f"Processing time: {processing_time:.6f} seconds")

        logging.debug("Audio, closing jaw")
        self.servo_controller.set_pulse_width(self.min_pulse_width)

    def start(self, audio_file):
        # Start audio analysis in a separate thread
        audio_analysis_thread = Thread(target=self.analyze_audio)
        audio_analysis_thread.daemon = False  # Daemon thread will exit when the main program exits
        audio_analysis_thread.start()

        self.analyzing = True

        # Play the audio file in the main thread
        play_audio(audio_file)

        # Stop analyzing when audio is done playing
        self.analyzing = False
