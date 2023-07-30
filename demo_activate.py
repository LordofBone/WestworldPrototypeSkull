import argparse
import logging
from time import sleep

from EventHive.event_hive_runner import EventQueue

from components.jaw_system import AudioJawSync
from components.microwave_sensor_runner import MicrowaveDetector
from components.tts_system import TTSOperations
from components.conversation_engine import ConversationEngine
from components.resource_monitor_leds import LedResourceMonitor

BOOT_SPLIT_WAIT = 5


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--log',
        default="info",
        help='Set the logging level (default: %(default)s)',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )
    return parser.parse_args()


args = parse_args()
numeric_level = getattr(logging, args.log.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {args.log}')
logging.getLogger().setLevel(numeric_level)


def main():
    logging.debug("Setting up systems")

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
