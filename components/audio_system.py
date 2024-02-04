import logging
from pathlib import Path
from threading import Condition

import pyaudio
from playsound import playsound

from config.tts_config import audio_on, file_name

logger = logging.getLogger(__name__)

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

        self.p = pyaudio.PyAudio()

        self.microphones = {}
        self.recording_streams = {}

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

        logger.debug("Initialized")

    def set_microphone_name(self, mic_key, mic_name):
        self.microphones[mic_key] = mic_name
        input_device = int(self.find_input_device(mic_name))

        self.RATE = self.find_compatible_sample_rate(input_device)
        self.CHUNK = self.find_compatible_chunk_size(input_device)

        # Store the RATE and CHUNK values in a dictionary for each microphone
        self.microphones[mic_key] = {
            'name': mic_name,
            'device': input_device,
            'RATE': self.RATE,
            'CHUNK': self.CHUNK
        }

        logger.debug(
            f"Microphone {mic_key} set to {mic_name}, device: {input_device}, RATE: {self.RATE}, CHUNK: {self.CHUNK}")

    def find_input_device(self, mic_name):
        # List all audio devices
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)

            logger.debug(f"Device index: {info['index']} - {info['name']}")

            # Check if the device name contains "USB PnP Sound Device"
            if mic_name in info['name']:
                logger.debug(f"{mic_name} at index: {info['index']}")
                return info['index']

        # If the device was not found
        logger.debug(f"{mic_name} not found")
        raise Exception(f"{mic_name} not found, please ensure it is plugged in.")

    def find_compatible_sample_rate(self, input_device):
        # Check for supported sample rates
        for rate in self.sample_rates:
            try:
                is_supported = self.p.is_format_supported(rate,
                                                          input_device=input_device,
                                                          input_channels=1,
                                                          input_format=pyaudio.paInt16)
                logger.debug(f"  Sample rate {rate} is supported: {is_supported}")
                return rate
            except ValueError as err:
                logger.debug(f"  Sample rate {rate} is NOT supported: {err}")

    # Check for supported chunk sizes
    def find_compatible_chunk_size(self, input_device):
        for chunk_size in self.chunk_sizes:
            try:
                # Attempt to open a stream with the given chunk size
                # If this fails, it will throw an exception which is caught in the except block
                stream = self.p.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=self.RATE,  # Use the rate determined previously
                                     input=True,
                                     frames_per_buffer=chunk_size,
                                     input_device_index=input_device)

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

    def init_recording_stream(self, mic_key):
        mic_info = self.microphones.get(mic_key)
        logger.debug(f"Initializing recording stream for {mic_key}, mic_info: {mic_info}")
        if not mic_info:
            logger.error(f"Microphone {mic_key} not initialized")
            return

        if mic_key in self.recording_streams:
            logger.debug(f"Recording stream for {mic_key} already initialized")
            return

        self.recording_streams[mic_key] = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=mic_info['RATE'],
            input=True,
            frames_per_buffer=mic_info['CHUNK'],
            input_device_index=mic_info['device']
        )

    def read_recording_stream(self, mic_key):
        stream = self.recording_streams.get(mic_key)
        if not stream:
            logger.error(f"Recording stream for {mic_key} not initialized")
            return

        mic_info = self.microphones.get(mic_key)
        data = stream.read(mic_info['CHUNK'], exception_on_overflow=False)
        return data

    def close_recording_stream(self, mic_key):
        stream = self.recording_streams.get(mic_key)
        if not stream:
            logger.error(f"Recording stream for {mic_key} not initialized")
            return

        stream.close()
        del self.recording_streams[mic_key]
        logger.debug(f"Recording stream for {mic_key} closed")


def audio_engine_access():
    return AudioEngine()
