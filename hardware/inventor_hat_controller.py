from inventorhatmini import InventorHATMini, SERVO_1
from ioexpander import IN  # or IN_PU of a pull-up is wanted


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.servo = self.board.servos[servo_id]
        self.input_mode = IN


InventorHATCoreInit = InventorHATCore()
