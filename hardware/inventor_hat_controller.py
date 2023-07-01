from inventorhatmini import InventorHATMini, SERVO_1, NUM_LEDS


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.servo = self.board.servos[servo_id]


InventorHATCoreInit = InventorHATCore()
