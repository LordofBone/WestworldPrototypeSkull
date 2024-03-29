import logging
from abc import ABC, abstractmethod
from time import sleep

from EventHive.event_hive_runner import EventActor
from config.command_config import override_word, de_override_word
from config.custom_events import CommandCheckEvent, CommandCheckDoneEvent, ConversationDoneEvent
from config.tts_config import test_command_text, shutdown_text, reboot_text, no_command_text
from utils.string_ops import clean_text

logger = logging.getLogger(__name__)
logger.debug("Initialized")


# Define a generic interface for command operations
class CommandOperationsInterface(ABC):
    @abstractmethod
    def process_command(self, event_data):
        pass


# Implement the real command operations
class RealCommandOperations(CommandOperationsInterface):
    def __init__(self, event_producer):
        self.event_producer = event_producer

    def process_command(self, event_data):
        # Clean and normalize both input and comparison strings
        clean_event_data = clean_text(event_data)

        if clean_event_data == override_word:
            self.event_producer(CommandCheckDoneEvent(["OVERRIDE_COMMAND_FOUND"], 1))
        elif clean_event_data == de_override_word:
            self.event_producer(CommandCheckDoneEvent(["DE_OVERRIDE_COMMAND_FOUND"], 1))
        elif clean_event_data in ["SHUTDOWN", "SHUT DOWN", "shutdown", "shut down", "power off", "poweroff",
                                  "turn off"]:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", ["shutdown_command", shutdown_text]], 1))
            logger.debug("Command checker finished, event output: SHUTDOWN")
        elif clean_event_data in ["REBOOT", "restart", "reboot", "restart now", "reboot now"]:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", ["reboot_command", reboot_text]], 1))
            logger.debug("Command checker finished, event output: REBOOT")
        elif clean_event_data in ["TEST", "test", "test command"]:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", ["test_command", test_command_text]], 1))
            logger.debug("Command checker finished, event output: TEST COMMAND")
        else:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", ["no_command", no_command_text]], 1))
            logger.debug("Command checker finished, no commands detected")


# Implement the test command operations
class TestCommandOperations(CommandOperationsInterface):
    def __init__(self, event_producer):
        self.event_producer = event_producer

    def process_command(self, event_data):
        self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "test_command"], 1))
        logger.debug("Test mode: Skipping actual command processing")


class CommandCheckOperations(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        # self.command_processor = TestCommandOperations(self.produce_event) if test_mode \
        #     else RealCommandOperations(self.produce_event)
        # todo: leaving the test strategy in place for now but not using it, as we need commands to go through
        #  while testing; may need in future though
        self.command_processor = RealCommandOperations(self.produce_event)

    def check_and_process_commands(self, event_type=None, event_data=None):
        self.command_processor.process_command(event_data)
        sleep(1)
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))
        return True

    def get_event_handlers(self):
        return {
            "CHECK_VOICE_COMMANDS": self.check_and_process_commands
        }

    def get_consumable_events(self):
        return [CommandCheckEvent]
