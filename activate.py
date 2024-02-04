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
from components.stt_system import STTOperations
from components.chatbot_system import ChatbotOperations
from components.command_system import CommandCheckOperations
from components.pi_operations_system import PiOperations

BOOT_SPLIT_WAIT = 5

logger = logging.getLogger(__name__)


# Add argparse to handle command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Activate the system with optional modes.")
    parser.add_argument("--demo_mode", action="store_true", help="Run in demo mode")
    parser.add_argument("--test_mode", action="store_true", help="Run in full run test mode")
    return parser.parse_args()


def main():
    args = parse_arguments()
    demo_mode = args.demo_mode
    test_mode = args.test_mode

    modes = []
    if demo_mode:
        modes.append('demo')
    if test_mode:
        modes.append('test')

    mode_str = ', '.join(modes) if modes else 'normal'
    logger.debug(f"Setting up systems in {mode_str} mode")

    event_queue = EventQueue(sleep_time=1)
    systems = [
        LedResourceMonitor(),
        AudioDetector(event_queue, test_mode=test_mode),
        TTSOperations(event_queue, test_mode=test_mode),
        STTOperations(event_queue, test_mode=test_mode),
        AudioJawSync(event_queue, test_mode=test_mode),
        ChatbotOperations(event_queue, test_mode=test_mode),
        CommandCheckOperations(event_queue, test_mode=test_mode),
        PiOperations(event_queue, test_mode=test_mode),
        ConversationEngine(event_queue, demo_mode=demo_mode),
    ]

    logger.debug("Starting producer and consumer threads")

    try:
        for system in systems:
            logger.debug(f"Starting {system.__class__.__name__} thread")
            system.start()
            sleep(BOOT_SPLIT_WAIT)
            logger.debug(f"Started {system.__class__.__name__} thread")

        for system in systems[1:]:  # Skip LedResourceMonitor, it doesn't join
            logger.debug(f"Joining {system.__class__.__name__} thread")
            system.join()
            logger.debug(f"Joined {system.__class__.__name__} thread")

        logger.debug("All systems started and threads joined")

    except KeyboardInterrupt:
        systems[0].stop()  # Stop LedResourceMonitor


if __name__ == '__main__':
    main()
