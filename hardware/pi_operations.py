import logging
from subprocess import call
from time import sleep

from EventHive.event_hive_runner import EventActor
from config.custom_events import HardwareEvent

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class PiOperations(EventActor):
    def __post_init__(self):
        # todo: add extra raspberry pi operations here, temp checks etc.
        self.shutdown_wait_seconds = 5

    def shutdown(self):
        """
        Shutdown the Pi
        :return:
        """
        logger.debug(f"Switching Off in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo shutdown now', shell=True)

    def reboot(self):
        """
        Restart the Pi
        :return:
        """
        logger.debug(f"Restarting in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo reboot now', shell=True)

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers that this consumer can handle.
        :return:
        """
        return {
            ("SHUTDOWN",): self.shutdown,
            ("REBOOT",): self.reboot
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [HardwareEvent]
