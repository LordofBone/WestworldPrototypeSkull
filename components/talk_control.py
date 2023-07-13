import logging

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT
from EventHive.event_hive_runner import EventActor
from Lakul.integrate_stt import SpeechtoTextHandler
from config.custom_events import ListenEvent, TTSEvent, HardwareEvent
from config.nix_tts import *

logging.basicConfig()
logger = logging.getLogger(__name__)


class TalkController(EventActor):
    def __post_init__(self):
        """
        This is the main class that runs the STT and bot interaction.
        """
        self.STT_handler = SpeechtoTextHandler()

        self.ChatGPT_handler = IntegrateChatGPT()

        self.inference_output = None

        self.bot_response = None

    def speak_tts(self, text):
        """
        This function is used to speak custom text.
        :return:
        """
        self.produce_event(TTSEvent([text], 1))

    def speak_tts_bot_response(self):
        """
        This function is used to speak the bot response.
        :return:
        """
        self.produce_event(TTSEvent([self.bot_response], 1))

    def listen_stt(self):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """

        print("Listening")

        self.STT_handler.initiate_recording()

        print("Inferencing")

        self.inference_output = self.STT_handler.run_inference()

        print("DONE")

        print(self.inference_output)
        logger.debug(self.inference_output)

    def command_checker(self):
        """
        This function checks for commands.
        :return:
        """
        if self.inference_output == "SHUTDOWN":
            self.produce_event(TTSEvent([shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
        elif self.inference_output == "SHUT DOWN":
            self.produce_event(TTSEvent([shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
        elif self.inference_output == "REBOOT":
            self.produce_event(TTSEvent([reboot_text], 1))
            self.produce_event(HardwareEvent(["REBOOT"], 1))

    def get_bot_engine_response(self):
        """
        This function returns the bot response.
        :return:
        """
        self.ChatGPT_handler.set_text_input(self.inference_output)
        self.bot_response = self.ChatGPT_handler.get_chatgpt_response()

        print(self.bot_response)
        logger.debug(self.bot_response)

    def conversation_cycle(self):
        """
        This function runs the conversation cycle.
        :return:
        """
        self.listen_stt()
        self.command_checker()
        self.get_bot_engine_response()
        self.speak_tts_bot_response()

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
        return [ListenEvent]
