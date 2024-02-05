import logging

from EventHive.event_hive_runner import EventActor
from config.conversation_config import conversation_function_list, demo_mode_function_list, command_function_list
from config.custom_events import (STTEvent, TTSEvent, BotEvent, MovementEvent, DetectEvent, STTDoneEvent, BotDoneEvent,
                                  ConversationDoneEvent, AudioDetectControllerEvent, CommandCheckEvent,
                                  CommandCheckDoneEvent, HardwareEvent)
from config.path_config import tts_audio_path
from config.tts_config import demo_text, greeting_text, override_text

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

        self.inference_output = None

        self.command_mode = False
        self.run_command = None

        self.bot_response = greeting_text
        self.stored_bot_response = greeting_text

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

    def set_inference_output(self, event_type=None, event_data=None):
        """
        This function sets the inference output.
        :param event_type:
        :param event_data:
        :return:
        """
        # Check if the string is empty or contains only whitespace
        if event_data.strip() == "":
            self.current_index = 0
            logger.debug("The inference output is empty, resetting action list index.")
        else:
            self.inference_output = event_data
            logger.debug(f"Retrieved Speech to Text output and set output response to: {self.inference_output}")

        return True

    def set_bot_response(self, event_type=None, event_data=None):
        """
        This function sets the bot response.
        :param event_type:
        :param event_data:
        :return:
        """
        # Check if the string is empty or contains only whitespace
        if event_data.strip() == "":
            self.current_index = 0
            logger.debug("The bot response is empty, resetting action list index.")
        else:
            self.bot_response = event_data
            logger.debug(f"Retrieved bot response and set output response to: {self.bot_response}")

        return True

    def get_bot_engine_response(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """
        self.produce_event(BotEvent(["GET_BOT_RESPONSE", self.inference_output], 1))
        logger.debug(f"Bot event produced with input: {self.inference_output}")

        return True

    def activate_jaw_audio(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """
        self.produce_event(MovementEvent(["JAW_TTS_AUDIO", tts_audio_path], 1))
        logger.debug(f"Jaw audio event produced with audio file: {tts_audio_path}")

        return True

    def command_checker(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """
        self.produce_event(CommandCheckEvent(["CHECK_VOICE_COMMANDS", self.inference_output], 1))
        logger.debug(f"Command check event produced with input: {self.inference_output}")

        return True

    def activate_command_system(self, event_type=None, event_data=None):
        """
        This function activates the command conversation system by setting the action list to loop and execute commands.
        :return:
        """
        self.command_mode = True
        self.stored_bot_response = self.bot_response
        self.reset_action_list()
        self.bot_response = override_text
        self.functions_list = command_function_list

        logger.debug(f"Command system online, with response: {self.bot_response} and functions list: "
                     f"{self.functions_list}")

        return True

    def de_activate_command_system(self, event_type=None, event_data=None):
        """
        This function activates the command conversation system by setting the action list to loop and execute commands.
        :return:
        """
        self.command_mode = False
        self.reset_action_list()
        self.bot_response = self.stored_bot_response
        self.functions_list = conversation_function_list

        logger.debug(f"Command system offline, with response: {self.bot_response} and "
                     f"functions list: {self.functions_list}")

        return True

    def set_command(self, event_type=None, event_data=None):
        """
        This function sets the command to run.
        :return:
        """
        if self.command_mode:
            self.run_command = event_data[0]
            self.bot_response = event_data[1]
            logger.debug(f"Command mode on, command set to: {self.run_command}")
        else:
            logger.debug("Command mode off, no command set.")

        return True

    def execute_command(self, event_type=None, event_data=None):
        """
        This function executes the command set previously.
        :param event_type:
        :param event_data:
        :return:
        """
        if self.run_command == "shutdown_command":
            self.produce_event(HardwareEvent(["SHUTDOWN"], 3))
            logger.debug("Command checker finished, event output: SHUTDOWN")
        elif self.run_command == "reboot_command":
            self.produce_event(HardwareEvent(["SHUTDOWN"], 3))
            logger.debug("Command checker finished, event output: REBOOT")
        elif self.run_command == "test_command":
            self.produce_event(HardwareEvent(["SHUTDOWN"], 3))
            logger.debug("Command checker finished, event output: TEST COMMAND")
        elif self.run_command == "no_command":
            logger.debug("No command to run.")
            self.next_action()
        else:
            logger.debug("No command to run.")
            self.next_action()

        return True

    def reset_action_list(self, event_type=None, event_data=None):
        """
        This function returns the bot response.
        :return:
        """

        self.functions_list = []
        self.current_index = 0

        logger.debug(f"All functions have been executed, action list and index reset to {self.current_index}")

    def conversation_cycle(self, event_type=None, event_data=None):
        """
        This function runs the conversation cycle.
        :return:
        """

        if self.demo_mode:
            self.functions_list = demo_mode_function_list
            self.bot_response = demo_text
        else:
            self.functions_list = conversation_function_list

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
        logger.debug(f"Next action called, with functions list: {self.functions_list}, current index: "
                     f"{self.current_index}")
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
                self.reset_action_list()

                return True
        else:
            logger.debug("No functions to execute.")

            return True
            # Optionally, you can add additional logic here if needed when the list is empty.

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "HUMAN_DETECTED": self.conversation_cycle,
            "CONVERSATION_ACTION_FINISHED": self.next_action,
            "STT_FINISHED": self.set_inference_output,
            "BOT_FINISHED": self.set_bot_response,
            "OVERRIDE_COMMAND_FOUND": self.activate_command_system,
            "DE_OVERRIDE_COMMAND_FOUND": self.de_activate_command_system,
            "COMMAND_FOUND": self.set_command,
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [DetectEvent, ConversationDoneEvent, STTDoneEvent, BotDoneEvent, CommandCheckDoneEvent]
