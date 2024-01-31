import logging

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT, IntegrateOllama
from EventHive.event_hive_runner import EventActor
from config.chattinggpt_config import openai_api_key, role, chat_backend, use_history, ollama_model
from config.custom_events import (STTEvent, TTSEvent, HardwareEvent, MovementEvent, DetectEvent, STTDoneEvent,
                                  ConversationDoneEvent, AudioDetectControllerEvent)
from config.path_config import tts_audio_path
from config.tts_config import shutdown_text, reboot_text, demo_text

logger = logging.getLogger(__name__)


class ConversationEngine(EventActor):
    def __init__(self, event_queue, demo_mode=True):
        super().__init__(event_queue)

        """
        This is the main class that runs the STT and bot interaction.
        """
        self.demo_mode = demo_mode

        self.functions_list = []

        self.current_index = 0

        if chat_backend == "gpt":
            self.ChatGPT_handler = IntegrateChatGPT(openai_api_key=openai_api_key, role=role, use_history=use_history)
        elif chat_backend == "ollama":
            self.ChatGPT_handler = IntegrateOllama(model=ollama_model, role=role, use_history=use_history)

        self.inference_output = None

        self.bot_response = None

        self.produce_event(AudioDetectControllerEvent(["SCAN_MODE_ON"], 1))

        logger.debug("Initialized")

    def speak_tts(self, text, event_type=None, event_data=None):
        """
        This function is used to speak custom text.
        :return:
        """
        self.produce_event(TTSEvent(["TALK"], 1))

        logger.debug(f"TTS event produced with text: {text}")

        return True

    def generate_tts_bot_response(self, event_type=None, event_data=None):
        """
        This function is used to speak the bot response.
        :return:
        """

        self.produce_event(TTSEvent(["GENERATE_TTS", self.bot_response], 1))

        logger.debug(f"TTS event produced with text: {self.bot_response}")

        return True

    def scan_mode_on(self, event_type=None, event_data=None):
        """
        This function is used to speak the bot response.
        :return:
        """

        self.produce_event(AudioDetectControllerEvent(["SCAN_MODE_ON"], 1))

        logger.debug("Bot is waiting to detect human presence by listening for noise.")

        return True

    def listen_stt(self, event_type=None, event_data=None):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """

        self.produce_event(STTEvent(["RECORD_INFER_SPEECH"], 1))

        logger.debug("STT event produced, recording and inferring speech.")

        return True

    def set_bot_response(self, event_type=None, event_data=None):
        self.inference_output = event_data

        logger.debug(f"Retrieved Speech to Text output and set bot response to: {self.inference_output}")

    def command_checker(self, event_type=None, event_data=None):
        """
        This function checks for commands.
        :return:
        """
        if self.inference_output == "SHUTDOWN":
            self.produce_event(TTSEvent(["GENERATE_TTS", shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
            logger.debug("Command checker finished, event output: SHUTDOWN")
        elif self.inference_output == "SHUT DOWN":
            self.produce_event(TTSEvent(["GENERATE_TTS", shutdown_text], 1))
            self.produce_event(HardwareEvent(["SHUTDOWN"], 1))
            logger.debug("Command checker finished, event output: SHUTDOWN")
        elif self.inference_output == "REBOOT":
            self.produce_event(TTSEvent(["GENERATE_TTS", reboot_text], 1))
            self.produce_event(HardwareEvent(["REBOOT"], 1))
            logger.debug("Command checker finished, event output: REBOOT")
        else:
            logger.debug("Command checker finished, no commands detected")

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
        logger.debug(f"Jaw audio event produced with audio file: {tts_audio_path}")

        return True

    def reset_action_list(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """

        self.functions_list = []
        self.current_index = 0

        logger.debug("All functions have been executed, action list and index reset.")

        return True

    def conversation_cycle(self, event_type=None, event_data=None):
        """
        This function runs the conversation cycle.
        :return:
        """

        if self.demo_mode:
            self.functions_list = [
                'generate_tts_bot_response',
                'activate_jaw_audio',
                'scan_mode_on',
            ]
            self.bot_response = demo_text
        else:
            logger.debug("Conversation activated")
            self.functions_list = [
                'generate_tts_bot_response',
                'activate_jaw_audio',
                'listen_stt',
                'generate_tts_bot_response',
                'activate_jaw_audio',
                'scan_mode_on',
            ]
            self.bot_response = "Listening"

        logger.debug(f"Conversation activated, demo mode: {self.demo_mode} "
                     f"with response: {self.bot_response} and functions list: {self.functions_list}")

        self.next_action()

        return True

    def next_action(self, event_type=None, event_data=None):
        """
        This function runs the next action.
        Some things we want to run asynchronously, but there are certain actions that rely on the completion of prior
        actions. This function is used to run the next action in the list (generated prior to calling this)
        and make sure that the previous action has completed.
        :param event_type:
        :param event_data:
        :return:
        """
        logger.debug(f"Next action called, with functions list: {self.functions_list}")
        if self.functions_list:  # This checks if the list is not empty
            if self.current_index < len(self.functions_list):
                func_name = self.functions_list[self.current_index]
                logger.debug(
                    f"Running next action: {func_name}, current index: {self.current_index}, "
                    f"total length: {len(self.functions_list)}")
                self.current_index += 1
                func = getattr(self, func_name)
                func()

                return True
            else:
                self.functions_list = []
                self.current_index = 0

                logger.debug("All functions have been executed, action list and index reset.")

                return True
        else:
            logger.debug("No functions to execute.")
            # Optionally, you can add additional logic here if needed when the list is empty.

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "HUMAN_DETECTED": self.conversation_cycle,
            "CONVERSATION_ACTION_FINISHED": self.next_action,
            "STT_FINISHED": self.set_bot_response,
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [DetectEvent, ConversationDoneEvent, STTDoneEvent]
