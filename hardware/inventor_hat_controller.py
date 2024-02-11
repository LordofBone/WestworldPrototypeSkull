import logging

from inventorhatmini import InventorHATMini, SERVO_1, NUM_LEDS
from ioexpander import IN  # or IN_PU if a pull-up is wanted

logger = logging.getLogger(__name__)
logger.debug("Initialized")


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.leds = self.board.leds
        self.servo = self.board.servos[servo_id]
        self.input_mode = IN
        self.num_leds = NUM_LEDS


InventorHATCoreInit = InventorHATCore()
