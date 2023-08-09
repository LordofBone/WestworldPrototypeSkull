import logging

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT
from EventHive.event_hive_runner import EventActor
from Lakul.integrate_stt import SpeechtoTextHandler
from config.custom_events import TTSEvent, HardwareEvent, MovementEvent, DetectEvent, TTSDoneEvent
from config.nix_tts import shutdown_text, reboot_text, demo_text
from config.path_config import tts_audio_path
from config.skull_config import microphone_name, role

from better_profanity import profanity

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class ConversationEngine(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        """
        This is the main class that runs the STT and bot interaction.
        """

        self.STT_handler = SpeechtoTextHandler(microphone_name)

        self.ChatGPT_handler = IntegrateChatGPT(role=role, use_history=True)

        self.inference_output = None

        self.bot_response = None

    def speak_tts(self, text, event_type=None, event_data=None):
        """
        This function is used to speak custom text.
        :return:
        """
        self.produce_event(TTSEvent(["TALK"], 1))

        return True

    def speak_tts_bot_response(self, event_type=None, event_data=None):
        """
        This function is used to speak the bot response.
        :return:
        """
        self.produce_event(TTSEvent([self.bot_response], 1))

        return True

    def listen_stt(self, event_type=None, event_data=None):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """

        logger.debug("Listening")

        self.STT_handler.initiate_recording()

        logger.debug("Inferencing")

        unfiltered_inference_output = self.STT_handler.run_inference()

        self.inference_output = profanity.censor(unfiltered_inference_output, '-')

        logger.debug("Finished inferencing")

        logger.debug(f"Inference output: {self.inference_output}")
        logger.debug(self.inference_output)

        return True

    def command_checker(self, event_type=None, event_data=None):
        """
        This function checks for commands.
        :return:
        """
        if self.inference_output == "SHUTDOWN":
            self.produce_event(TTSEvent(["GENERATE_TTS", shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
        elif self.inference_output == "SHUT DOWN":
            self.produce_event(TTSEvent(["GENERATE_TTS", shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
        elif self.inference_output == "REBOOT":
            self.produce_event(TTSEvent(["GENERATE_TTS", reboot_text], 1))
            self.produce_event(HardwareEvent(["REBOOT"], 1))

        return True

    def get_bot_engine_response(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """
        self.bot_response = self.ChatGPT_handler.get_response(self.inference_output)
        logger.debug(f"Bot response: {self.bot_response}")
        return True

    def activate_jaw_audio(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """

        self.produce_event(MovementEvent(["JAW_TTS_AUDIO", tts_audio_path], 1))
        return True

    def conversation_cycle(self, event_type=None, event_data=None):
        """
        This function runs the conversation cycle.
        :return:
        """
        self.listen_stt()
        self.command_checker()
        self.get_bot_engine_response()
        self.speak_tts_bot_response()

    def conversation_cycle_demo(self, event_type=None, event_data=None):
        """
        This function runs the conversation cycle.
        :return:
        """
        logger.debug("Demo mode activated")
        self.produce_event(TTSEvent(["GENERATE_TTS", demo_text], 1))
        return True

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "HUMAN_DETECTED_DEMO": self.conversation_cycle_demo,
            "HUMAN_DETECTED": self.conversation_cycle,
            "TTS_GENERATION_FINISHED": self.activate_jaw_audio
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [DetectEvent, TTSDoneEvent]
