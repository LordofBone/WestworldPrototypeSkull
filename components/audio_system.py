import logging
from pathlib import Path
from threading import Condition

import pyaudio
from playsound import playsound

from config.nix_tts import audio_on, file_name
from config.skull_config import microphone_name

logger = logging.getLogger(__name__)
logger.debug("Initialized")

condition = Condition()


def ensure_not_talking(func):
    """
    Decorator function to make sure the audio engine isn't currently talking before allowing it to start talking again.
    The decorator also handles setting the 'talking' state.
    """

    def wrapper(*args, **kwargs):
        with condition:
            while audio_engine_access().talking:
                condition.wait()

            audio_engine_access().talking = True
            logger.debug(f'Set talking state to: {audio_engine_access().talking}')

        result = func(*args, **kwargs)

        with condition:
            audio_engine_access().talking = False
            condition.notify_all()
            logger.debug(f'Set talking state to: {audio_engine_access().talking}')

        return result

    return wrapper


class AudioEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioEngine, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        self.microphone_name = microphone_name

        self.p = pyaudio.PyAudio()

        self.sample_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 384000]
        self.chunk_sizes = [128, 256, 512, 1024, 2048]

        self.input_device = None

        self.RATE = None
        self.CHUNK = None

        self._recording_stream = None
        self.talking = False

        self.path = Path(__file__).parent / "../audio"
        self.audio_on = audio_on

        self.audio_file = self.path / file_name
        self.online = self.path / "online.wav"
        self.training = self.path / "training.wav"

    def set_microphone_name(self, mic_name="Microphone"):
        self.microphone_name = mic_name
        self.input_device = int(self.find_usb_microphone_device())

        self.RATE = self.find_compatible_sample_rate()
        self.CHUNK = self.find_compatible_chunk_size()

    def find_usb_microphone_device(self):
        # List all audio devices
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)

            logger.debug(f"Device index: {info['index']} - {info['name']}")

            # Check if the device name contains "USB PnP Sound Device"
            if self.microphone_name in info['name']:
                logger.debug(f"{self.microphone_name} at index: {info['index']}")
                return info['index']

        # If the device was not found
        logger.debug(f"{self.microphone_name} not found")
        raise Exception(f"{self.microphone_name} not found, please ensure it is plugged in.")

    def find_compatible_sample_rate(self):
        # Check for supported sample rates
        for rate in self.sample_rates:
            try:
                is_supported = self.p.is_format_supported(rate,
                                                          input_device=self.input_device,
                                                          input_channels=1,
                                                          input_format=pyaudio.paInt16)
                logger.debug(f"  Sample rate {rate} is supported: {is_supported}")
                return rate
            except ValueError as err:
                logger.debug(f"  Sample rate {rate} is NOT supported: {err}")

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
                logger.debug(f"  Chunk size {chunk_size} is supported.")
                return chunk_size
            except Exception as err:
                # This chunk size is not supported. Continue checking the next one.
                logger.debug(f"  Chunk size {chunk_size} is NOT supported: {err}")

    @ensure_not_talking
    def play_audio(self):
        """
        This function is used to play the generated TTS output.
        """
        if self.audio_on:
            playsound(self.audio_file)

    def init_recording_stream(self):
        if self._recording_stream is not None:
            logger.debug("Recording stream already initialized")
            return
        else:
            logger.debug("Initializing recording stream")
            self._recording_stream = self.p.open(format=pyaudio.paInt16,
                                                 channels=1,
                                                 rate=self.RATE,
                                                 input=True,
                                                 frames_per_buffer=self.CHUNK,
                                                 input_device_index=self.input_device)

    def read_recording_stream(self):
        """
        This function is used to read the audio input from the microphone.
        """
        if self._recording_stream is None:
            logger.debug("Recording stream not initialized")
            return
        else:
            data = self._recording_stream.read(self.CHUNK, exception_on_overflow=False)
            return data

    def close_recording_stream(self):
        if self._recording_stream is None:
            logger.debug("Recording stream not initialized")
        else:
            self._recording_stream.close()
            self._recording_stream = None
            logger.debug("Recording stream closed")


def audio_engine_access():
    return AudioEngine()
