from EventHive.event_hive_runner import EventActor
from config.custom_events import DetectEvent

from hardware.inventor_hat_controller import InventorHATCoreInit

InventorHATCoreInit.board.gpio_pin_mode(0, InventorHATCoreInit.input_mode)


class MicrowaveDetector(EventActor):
    def run(self):
        while True:
            if InventorHATCoreInit.board.gpio_pin_value(0):
                self.produce_event(DetectEvent(["HUMAN_DETECTED"], 1))

    def get_event_handlers(self):
        # No event handlers for the Producer since it's not supposed to consume any events.
        return {}

    def get_consumable_events(self):
        # No consumable events for the Producer since it's not supposed to consume any events.
        return []
