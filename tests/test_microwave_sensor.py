from time import sleep
from datetime import datetime
from inventorhatmini import InventorHATMini, SERVO_1, NUM_LEDS
from ioexpander import IN  # or IN_PU of a pull-up is wanted


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.leds = self.board.leds
        self.servo = self.board.servos[servo_id]
        self.input_mode = IN
        self.num_leds = NUM_LEDS


InventorHATCoreInit = InventorHATCore()

InventorHATCoreInit.board.gpio_pin_mode(0, InventorHATCoreInit.input_mode)

while True:
    if InventorHATCoreInit.board.gpio_pin_value(0):
        print(f"{datetime.now()}: DETECTED")
        sleep(2)
