import logging
import threading
from time import sleep

from EventHive.event_hive_runner import EventActor
from config.custom_events import DetectEvent, MicrowaveControllerEvent
from hardware.inventor_hat_controller import InventorHATCoreInit

InventorHATCoreInit.board.gpio_pin_mode(0, InventorHATCoreInit.input_mode)

logger = logging.getLogger(__name__)


class MicrowaveDetector(EventActor):
    def __init__(self, event_queue, demo_mode=True):
        super().__init__(event_queue)
        self.scan_mode_enabled = demo_mode

        # Spawn a new thread to run the microwave scan function
        self.scan_thread = threading.Thread(target=self.microwave_scan, daemon=True)
        self.scan_thread.start()

    def microwave_scan(self):
        while True:
            if InventorHATCoreInit.board.gpio_pin_value(0):
                if self.scan_mode_enabled:
                    self.produce_event(DetectEvent(["HUMAN_DETECTED"], 1))
                    logging.debug("Movement detected")
                    self.scan_mode_off()
                    sleep(2)

    def scan_mode_on(self, event_type=None, event_data=None):
        logging.debug("SCAN MODE ON")
        self.scan_mode_enabled = True
        return True

    def scan_mode_off(self, event_type=None, event_data=None):
        logging.debug("SCAN MODE OFF")
        self.scan_mode_enabled = False
        return True

    def get_event_handlers(self):
        return {
            "SCAN_MODE_ON": self.scan_mode_on,
            "SCAN_MODE_OFF": self.scan_mode_off
        }

    def get_consumable_events(self):
        return [MicrowaveControllerEvent]
