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
        self.input_device = self.find_usb_microphone_device()

        self.servo_controller = JawController()
        self.servo_controller.open_jaw()
        self.analyzing = True
        self.max_rms = 1
        self.smoothed_rms = 0
        self.alpha = 0.8  # Smoothing factor (between 0 and 1)

        # Audio settings
        self.sample_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 384000]
        self.chunk_sizes = [128, 256, 512, 1024, 2048]
        self.RATE = self.find_compatible_sample_rate()  # Find lowest compatible sample rate
        self.CHUNK = self.find_compatible_chunk_size()  # Reduced chunk size
        self.max_rms = 50  # Set the maximum RMS value to 55

        # Normalize RMS value to desired pulse width range (25 to 75)
        self.min_pulse_width = 25
        self.max_pulse_width = 75

    def find_usb_microphone_device(self):
        # List all audio devices
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            print(f"Device index: {info['index']} - {info['name']}")

            # Check if the device name contains "USB PnP Sound Device"
            if "USB PnP Sound Device" in info['name']:
                print("Found USB PnP Sound Device at index:", info['index'])
                return info['index']

        # If the device was not found
        print("USB PnP Sound Device not found")
        return None

    def find_compatible_sample_rate(self):
        # Check for supported sample rates
        for rate in self.sample_rates:
            try:
                is_supported = self.p.is_format_supported(rate,
                                                          input_device=self.input_device,
                                                          input_channels=1,
                                                          input_format=pyaudio.paInt16)
                print(f"  Sample rate {rate} is supported: {is_supported}")
                return rate
            except ValueError as err:
                print(f"  Sample rate {rate} is NOT supported: {err}")

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
                print(f"  Chunk size {chunk_size} is supported.")
                return chunk_size
            except Exception as err:
                # This chunk size is not supported. Continue checking the next one.
                print(f"  Chunk size {chunk_size} is NOT supported: {err}")

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

            normalized_rms = rms / self.max_rms
            pulse_width = (normalized_rms * (self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width

            print(f"RMS: {rms} | Pulse width: {pulse_width}")

            # Set pulse width
            self.servo_controller.set_pulse_width(pulse_width)

            # Print processing time
            end_time = time.time()  # Record the end time
            processing_time = end_time - start_time
            print(f"Processing time: {processing_time:.6f} seconds")

    def start(self, audio_file):
        # Start audio analysis in a separate thread
        audio_analysis_thread = Thread(target=self.analyze_audio)
        audio_analysis_thread.daemon = True  # Daemon thread will exit when the main program exits
        audio_analysis_thread.start()

        # Play the audio file in the main thread
        play_audio(audio_file)

        # Stop analyzing when audio is done playing
        self.analyzing = False
