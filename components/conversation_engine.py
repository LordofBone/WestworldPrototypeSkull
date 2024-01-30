import logging

from better_profanity import profanity

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT, IntegrateOllama
from EventHive.event_hive_runner import EventActor
from Lakul.integrate_stt import SpeechtoTextHandler
from config.audio_config import microphone_name
from config.chattinggpt_config import openai_api_key, role, chat_backend, use_history, ollama_model
from config.custom_events import TTSEvent, HardwareEvent, MovementEvent, DetectEvent, TTSDoneEvent, \
    AudioDetectControllerEvent
from config.path_config import tts_audio_path
from config.tts_config import shutdown_text, reboot_text, demo_text

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class ConversationEngine(EventActor):
    def __init__(self, event_queue, demo_mode=True):
        super().__init__(event_queue)

        """
        This is the main class that runs the STT and bot interaction.
        """
        self.demo_mode = demo_mode

        self.functions_list = []

        self.current_index = 0

        self.STT_handler = SpeechtoTextHandler(microphone_name)

        if chat_backend == "gpt":
            self.ChatGPT_handler = IntegrateChatGPT(openai_api_key=openai_api_key, role=role, use_history=use_history)
        elif chat_backend == "ollama":
            self.ChatGPT_handler = IntegrateOllama(model=ollama_model, role=role, use_history=use_history)

        self.inference_output = None

        self.bot_response = None

        self.produce_event(AudioDetectControllerEvent(["SCAN_MODE_ON"], 1))

    def speak_tts(self, text, event_type=None, event_data=None):
        """
        This function is used to speak custom text.
        :return:
        """
        self.produce_event(TTSEvent(["TALK"], 1))

        return True

    def generate_tts_bot_response(self, event_type=None, event_data=None):
        """
        This function is used to speak the bot response.
        :return:
        """

        self.produce_event(TTSEvent(["GENERATE_TTS", self.bot_response], 1))

        return True

    def scan_mode_on(self, event_type=None, event_data=None):
        """
        This function is used to speak the bot response.
        :return:
        """

        self.produce_event(AudioDetectControllerEvent(["SCAN_MODE_ON"], 1))

        return True

    def listen_stt(self, event_type=None, event_data=None):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """
        print("Finished speaking")

        logger.debug("Listening")

        self.STT_handler.initiate_recording(max_seconds=60, silence_threshold=1000, silence_duration=2000)

        logger.debug("Inferencing")

        unfiltered_inference_output = self.STT_handler.run_inference()

        logger.debug(f"Unfiltered inference output: {unfiltered_inference_output}")

        self.inference_output = profanity.censor(unfiltered_inference_output, '-')

        logger.debug("Finished inferencing")

        logger.debug(f"Inference output: {self.inference_output}")

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
        logging.debug(f"Jaw audio activated with audio file: {tts_audio_path}")

        return True

    def reset_action_list(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """
        logger.debug("All functions have been executed.")
        self.functions_list = []
        self.current_index = 0

        return True

    def conversation_cycle(self, event_type=None, event_data=None):
        """
        This function runs the conversation cycle.
        :return:
        """

        if self.demo_mode:
            logger.debug("Demo mode activated")
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
        logging.debug(f"Next action called, with functions list: {self.functions_list}")
        if self.functions_list:  # This checks if the list is not empty
            if self.current_index < len(self.functions_list):
                func_name = self.functions_list[self.current_index]
                logger.debug(
                    f"Running next action: {func_name}, current index: {self.current_index}, total length: {len(self.functions_list)}")
                self.current_index += 1
                func = getattr(self, func_name)
                func()

                return True
            else:
                logger.debug("All functions have been executed.")
                self.functions_list = []
                self.current_index = 0

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
            # "TTS_GENERATION_FINISHED": self.activate_jaw_audio,
            "CONVERSATION_ACTION_FINISHED": self.next_action,
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [DetectEvent, TTSDoneEvent]
