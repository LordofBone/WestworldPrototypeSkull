import argparse
import importlib
import logging
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import soundfile as sf

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))
from config.tts_config import nix_dir, audio_dir, file_name as default_file_name, stoch_model_path

sys.path.append(nix_dir)

logger = logging.getLogger(__name__)

# Setup argument parser
parser = argparse.ArgumentParser(description="Generate TTS from text input.")
parser.add_argument("--file_name", type=str, default=default_file_name,
                    help="The name of the file to save the TTS audio. Default is set in config.")
parser.add_argument("--text", type=str, default="Testing Whisper speech to text",
                    help="The text to convert to speech. Defaults to 'Testing Whisper speech to text'.")

args = parser.parse_args()

# Update logger to include file_name and text input from args for clarity
logger.debug(f"Initialized with file_name: {args.file_name} and text: '{args.text}'")


class AbstractTTSOperations(ABC):
    @abstractmethod
    def generate_tts(self, text_input):
        pass


class TTSOperationsNix(AbstractTTSOperations):
    def __init__(self, filename):
        self.filename = filename
        self.sampling_frequency = 22050

        mod = importlib.import_module('nix-tts.nix.models.TTS')
        klass = getattr(mod, 'NixTTSInference')
        self.nix_tts = klass(model_dir=stoch_model_path)

    def generate_tts(self, text_input):
        c, c_length, phoneme = self.nix_tts.tokenize(text_input)
        xw = self.nix_tts.vocalize(c, c_length)
        sf.write(self.filename, xw[0, 0], self.sampling_frequency)


# Use the args to initialize and run TTS
tts_generator = TTSOperationsNix(f'{audio_dir}/{args.file_name}')
tts_generator.generate_tts(args.text)
