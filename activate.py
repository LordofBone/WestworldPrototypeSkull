import argparse
import logging
from time import sleep

from config.path_config import setup_paths
from utils.logging_system import activate_logging_system
activate_logging_system()
setup_paths()
from EventHive.event_hive_runner import EventQueue
from components.conversation_engine import ConversationEngine
from components.jaw_system import AudioJawSync
from components.audio_detector_runner import AudioDetector
from components.resource_monitor_leds import LedResourceMonitor
from components.tts_system import TTSOperations

BOOT_SPLIT_WAIT = 5

logger = logging.getLogger(__name__)


# Add argparse to handle command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the ChattingGPT system.")
    parser.add_argument("--demo_mode", action="store_true", help="Run in demo mode")
    return parser.parse_args()


def main():
    args = parse_arguments()
    demo_mode = args.demo_mode
    logger.debug(f"Setting up systems in {'demo' if demo_mode else 'normal'} mode")

    event_queue = EventQueue()
    systems = [
        LedResourceMonitor(),
        AudioDetector(event_queue),
        TTSOperations(event_queue),
        AudioJawSync(event_queue),
        ConversationEngine(event_queue, demo_mode=demo_mode),
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
