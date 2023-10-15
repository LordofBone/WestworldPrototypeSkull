import importlib
import logging
import sys
from abc import ABC, abstractmethod

from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

import soundfile as sf

from config.tts_config import nix_dir, audio_dir, file_name, stoch_model_path

sys.path.append(nix_dir)

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class AbstractTTSOperations(ABC):
    @abstractmethod
    def generate_tts(self, text_input):
        pass


class TTSOperationsNix(AbstractTTSOperations):
    def __init__(self):
        self.filename = f'{audio_dir}/{file_name}'
        self.sampling_frequency = 22050

        mod = importlib.import_module('nix-tts.nix.models.TTS')
        klass = getattr(mod, 'NixTTSInference')
        self.nix_tts = klass(model_dir=stoch_model_path)

    def generate_tts(self, text_input):
        c, c_length, phoneme = self.nix_tts.tokenize(text_input)
        xw = self.nix_tts.vocalize(c, c_length)
        sf.write(self.filename, xw[0, 0], self.sampling_frequency)


if __name__ == "__main__":
    TTS_GENERATOR = TTSOperationsNix()
    # Get the user's desired text
    user_input = input("Please enter the text you want to generate TTS for (or type 'exit' to quit): ")
    TTS_GENERATOR.generate_tts(user_input)
    print("TTS generated for:", user_input)
