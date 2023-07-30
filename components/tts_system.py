import importlib
import logging
import sys

import pyttsx3
import soundfile as sf
from fakeyou.fakeyou import FakeYou

from EventHive.event_hive_runner import EventActor
from config.custom_events import TTSEvent, TTSDoneEvent
from config.fakeyou_config import username, password, voice_model
from config.nix_tts import *
from config.skull_config import tts_mode

logger = logging.getLogger(__name__)

sys.path.append(nix_dir)

mod = importlib.import_module('nix-tts.nix.models.TTS')
klass = getattr(mod, 'NixTTSInference')


class TTSOperations(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        self.filename = f'{audio_dir}/{file_name}'

        # Switch based on tts_mode
        if tts_mode == 'nix':
            self.tts = TTSOperationsNix()
            logging.debug("Nix initiated")

        elif tts_mode == 'fakeyou':
            self.tts = TTSOperationsFakeYou()
            logging.debug("FakeYou initiated")

        elif tts_mode == 'pyttsx3':
            self.tts = TTSOperationsPyTTSx3()
            logging.debug("PyTTSx3 initiated")

        else:
            raise ValueError(f'Invalid tts_mode: {tts_mode}')

    def generate_tts(self, event_type=None, event_data=None):
        """
        Generate TTS output.
        :param event_data:
        :param event_type:
        :return:
        """
        logging.debug(f"Generating TTS with event data: + {event_data} using tts_mode: {tts_mode}")

        # Defer to the relevant TTS service
        self.tts.generate_tts(event_data)
        self.produce_event(TTSDoneEvent(["TTS_GENERATION_FINISHED"], 1))

        return True

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "GENERATE_TTS": self.generate_tts
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [TTSEvent]


class TTSOperationsFakeYou:
    def __init__(self):
        self.tts_runner = FakeYou()
        self.tts_runner.login(username, password)

        self.filename = f'{audio_dir}/{file_name}'

    def generate_tts(self, text_input):
        """
        Generate TTS output.
        :param text_input:
        :return:
        """
        output = self.tts_runner.say(text_input, voice_model)

        output.save(self.filename)


class TTSOperationsPyTTSx3:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        logging.info(f"Voices: {self.voices}")

        self.engine.setProperty('voice', self.voices[2].id)

        self.filename = f'{audio_dir}/{file_name}'

    def generate_tts(self, text_input):
        """
        Generate TTS output.
        :param text_input:
        :return:
        """

        self.engine.save_to_file(text_input, self.filename)
        self.engine.runAndWait()


class TTSOperationsNix:
    def __init__(self):
        self.filename = f'{audio_dir}/{file_name}'
        self.sampling_frequency = 22050

        mod = importlib.import_module('nix-tts.nix.models.TTS')
        klass = getattr(mod, 'NixTTSInference')
        self.nix_tts = klass(model_dir=stoch_model_path)

    def generate_tts(self, text_input):
        """
        Generate TTS output.
        :param text_input:
        :return:
        """

        # Tokenize input text
        c, c_length, phoneme = self.nix_tts.tokenize(text_input)
        # Convert text to raw speech
        xw = self.nix_tts.vocalize(c, c_length)
        sf.write(self.filename, xw[0, 0], self.sampling_frequency)
