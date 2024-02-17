import importlib
import logging
import os
import sys
from abc import ABC, abstractmethod

import pyttsx3
import soundfile as sf
from dotenv import load_dotenv
from fakeyou.fakeyou import FakeYou
from openai import OpenAI

load_dotenv()

open_ai_api_key = os.getenv("OPENAI_API_KEY")

from EventHive.event_hive_runner import EventActor
from components.fakeyou_api import username, password, voice_model
from config.custom_events import TTSEvent, ConversationDoneEvent
from config.tts_config import (tts_mode, nix_dir, audio_dir, file_name, stoch_model_path, pyttsx3_voice, openai_model,
                               openai_voice)

sys.path.append(nix_dir)

logger = logging.getLogger(__name__)


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


class TTSOperationsOpenAI(AbstractTTSOperations):
    def __init__(self):
        self.client = OpenAI(
            api_key=open_ai_api_key,
        )
        self.filename = f'{audio_dir}/{file_name}'

    def generate_tts(self, text_input):
        response = self.client.audio.speech.create(
            model=openai_model,
            voice=openai_voice,
            input=text_input,
        )
        response.stream_to_file(self.filename)


class TTSOperationsFakeYou(AbstractTTSOperations):
    def __init__(self):
        self.tts_runner = FakeYou()
        self.tts_runner.login(username, password)
        self.filename = f'{audio_dir}/{file_name}'

    def generate_tts(self, text_input):
        output = self.tts_runner.say(text_input, voice_model)
        output.save(self.filename)


class TTSOperationsPyTTSx3(AbstractTTSOperations):
    # todo: seems this can be buggy on repeat runs, may need to investigate, remove or find a workaround
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[pyttsx3_voice].id)
        self.filename = f'{audio_dir}/{file_name}'

    def generate_tts(self, text_input):
        self.engine.save_to_file(text_input, self.filename)
        self.engine.runAndWait()


class TestTTSHandler(AbstractTTSOperations):
    def generate_tts(self, text_input):
        logger.debug("Test mode: Skipping actual TTS generation")


class TTSOperations(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        self.filename = f'{audio_dir}/{file_name}'

        tts_class_map = {
            'nix': TTSOperationsNix,
            'fakeyou': TTSOperationsFakeYou,
            'pyttsx3': TTSOperationsPyTTSx3,
            'openai': TTSOperationsOpenAI,
            'test': TestTTSHandler  # Handling test mode
        }

        self.tts = tts_class_map.get('test')() if test_mode else tts_class_map.get(tts_mode)()
        if self.tts is None:
            raise ValueError(f'Invalid tts_mode: {tts_mode}')
        logger.debug(f"Initialized with TTS mode: {self.tts.__class__.__name__}")

    def generate_tts(self, event_type=None, event_data=None):
        logger.info(f"Generating TTS with event data: {event_data} using tts_mode: {tts_mode}")
        self.tts.generate_tts(event_data)
        logger.info(f"TTS generated and saved to: {self.filename}")
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))
        return True

    def get_event_handlers(self):
        return {
            "GENERATE_TTS": self.generate_tts
        }

    def get_consumable_events(self):
        return [TTSEvent]

# todo: make this its own submodule repo one day
