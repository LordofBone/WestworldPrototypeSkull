import logging
from abc import ABC, abstractmethod
from time import sleep

from EventHive.event_hive_runner import EventActor
from config.command_config import override_word
from config.custom_events import CommandCheckEvent, CommandCheckDoneEvent, ConversationDoneEvent

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
        if event_data == override_word:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "override_command"], 1))
        elif event_data in ["SHUTDOWN", "SHUT DOWN"]:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "shutdown_command"], 1))
            logger.debug("Command checker finished, event output: SHUTDOWN")
        elif event_data == "REBOOT":
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "reboot_command"], 1))
            logger.debug("Command checker finished, event output: REBOOT")
        elif event_data == "TEST COMMAND":
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "test_command"], 1))
            logger.debug("Command checker finished, event output: TEST COMMAND")
        else:
            self.event_producer(CommandCheckDoneEvent(["COMMAND_FOUND", "no_command"], 1))
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
        self.command_processor = TestCommandOperations(self.produce_event) if test_mode \
            else RealCommandOperations(self.produce_event)

    def check_and_process_commands(self, event_type=None, event_data=None):
        self.command_processor.process_command(event_data)
        sleep(1)
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))
        return True

    def get_event_handlers(self):
        return {"CHECK_VOICE_COMMANDS": self.check_and_process_commands}

    def get_consumable_events(self):
        return [CommandCheckEvent]
