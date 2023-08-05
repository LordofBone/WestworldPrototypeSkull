import logging
from pathlib import Path

from playsound import playsound

# todo: move to more generic config
from config.nix_tts import audio_on, file_name

# Initialize logger with the given name
logger = logging.getLogger(__name__)
logger.debug("Initialized")


def ensure_not_talking(func):
    """
    Decorator function to make sure the audio engine isn't currently talking before allowing it to start talking again.
    The decorator also handles setting the 'talking' state.
    """

    def wrapper(*args, **kwargs):
        # Wait until the audio engine is finished talking
        while AudioEngineAccess.talking:
            pass

        # Set the audio engine to 'talking' state
        AudioEngineAccess.talking = True
        logger.debug(f'Set talking state to: {AudioEngineAccess.talking}')

        func(*args, **kwargs)

        # Set the audio engine back to 'not talking' state
        AudioEngineAccess.talking = False
        logger.debug(f'Set talking state to: {AudioEngineAccess.talking}')

    return wrapper


class AudioEngine:
    """
    The AudioEngine handles playing audio, primarily from TTS output.
    """

    def __init__(self):
        self.talking = False  # Tracks if the audio engine is currently talking

        self.path = Path(__file__).parent / "../audio"  # Base path for audio files
        self.audio_on = audio_on  # Whether audio should be played or not

        # Predefined audio files
        self.audio_file = self.path / file_name
        self.online = self.path / "online.wav"
        self.training = self.path / "training.wav"

    @ensure_not_talking
    def play_audio(self):
        """
        This function is used to play the generated TTS output.
        """
        if self.audio_on:
            playsound(self.audio_file)


# Initialize a globally accessible AudioEngine
AudioEngineAccess = AudioEngine()
