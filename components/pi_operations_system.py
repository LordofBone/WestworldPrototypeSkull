import logging
from abc import ABC, abstractmethod

from EventHive.event_hive_runner import EventActor
from config.custom_events import HardwareEvent, ConversationDoneEvent
from config.hardware_control_config import shutdown_wait_seconds
from hardware.linux_command_controller import LinuxCommandProcessor

logger = logging.getLogger(__name__)
logger.debug("Initialized")


# Define a generic interface for Pi operations
class PiOperationHandler(ABC):
    @abstractmethod
    def shutdown(self):
        pass

    @abstractmethod
    def reboot(self):
        pass


# Implement the real Pi operation handling
class RealPiOperationHandler(PiOperationHandler):
    def __init__(self):
        self.command_handler = LinuxCommandProcessor(shutdown_wait_seconds)

    def shutdown(self):
        logger.debug("Sent shutdown command to LinuxCommandProcessor")
        self.command_handler.shutdown()

    def reboot(self):
        logger.debug("Sent reboot command to LinuxCommandProcessor")
        self.command_handler.reboot()


# Implement the test Pi operation handling
class TestPiOperationHandler(PiOperationHandler):
    def shutdown(self):
        logger.debug("Test mode: Skipping actual shutdown")

    def reboot(self):
        logger.debug("Test mode: Skipping actual reboot")


class PiOperations(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        self.operation_handler = TestPiOperationHandler() if test_mode else RealPiOperationHandler()

    def shutdown(self, event_type=None, event_data=None):
        self.operation_handler.shutdown()
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))
        return True

    def reboot(self, event_type=None, event_data=None):
        self.operation_handler.reboot()
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))
        return True

    def get_event_handlers(self):
        return {
            "SHUTDOWN": self.shutdown,
            "REBOOT": self.reboot
        }

    def get_consumable_events(self):
        return [HardwareEvent]
