import logging

from utils import logging_system

from time import sleep

from EventHive.event_hive_runner import EventQueue
from components.conversation_engine import ConversationEngine
from components.jaw_system import AudioJawSync
from components.microwave_sensor_runner import MicrowaveDetector
from components.resource_monitor_leds import LedResourceMonitor
from components.tts_system import TTSOperations

BOOT_SPLIT_WAIT = 5

logger = logging.getLogger(__name__)


def main():
    logger.debug("Setting up systems")

    event_queue = EventQueue()
    systems = [
        LedResourceMonitor(),
        MicrowaveDetector(event_queue),
        TTSOperations(event_queue),
        AudioJawSync(event_queue),
        ConversationEngine(event_queue, demo_mode=True),
    ]

    logging.debug("Starting producer and consumer threads")

    try:
        for system in systems:
            system.start()
            sleep(BOOT_SPLIT_WAIT)

        logging.debug("Waiting for threads to finish")
        for system in systems[1:]:  # Skip LedResourceMonitor, it doesn't join
            system.join()

    except KeyboardInterrupt:
        systems[0].stop()  # Stop LedResourceMonitor


if __name__ == '__main__':
    main()
