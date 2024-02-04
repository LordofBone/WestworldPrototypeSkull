import logging
from subprocess import call
from time import sleep

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class LinuxCommandProcessor:
    def __init__(self, shutdown_wait_seconds=5):
        self.shutdown_wait_seconds = shutdown_wait_seconds

    def shutdown(self, event_type=None, event_data=None):
        """
        Shutdown the Pi
        :return:
        """
        logger.debug(f"Switching Off in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo shutdown now', shell=True)

    def reboot(self, event_type=None, event_data=None):
        """
        Restart the Pi
        :return:
        """
        logger.debug(f"Restarting in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo reboot now', shell=True)

    # todo: add extra raspberry pi operations here, temp checks etc.
