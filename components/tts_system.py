import importlib
import sys

import soundfile as sf

from EventHive.event_hive_runner import EventActor
from components.audio_system import AudioEngineAccess
from config.custom_events import TTSEvent
from config.nix_tts import *

sys.path.append(nix_dir)

mod = importlib.import_module('nix-tts.nix.models.TTS')
klass = getattr(mod, 'NixTTSInference')


class TTSOperations(EventActor):
    def __post_init__(self):
        self.sampling_frequency = 22050
        self.filename = f'{audio_dir}/{file_name}'

        # Initiate Nix-TTS
        self.nix = klass(model_dir=stoch_model_path)

    def generate_tts(self, text_input):
        """
        Generate TTS output.
        :param text_input:
        :return:
        """
        # Tokenize input text
        c, c_length, phoneme = self.nix.tokenize(text_input)
        # Convert text to raw speech
        xw = self.nix.vocalize(c, c_length)
        sf.write(self.filename, xw[0, 0], self.sampling_frequency)
        # Play TTS output
        AudioEngineAccess.play_tts()

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            ("CONVERSE",): self.conversation_cycle
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [TTSEvent]
