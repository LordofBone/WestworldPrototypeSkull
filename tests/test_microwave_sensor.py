from time import sleep, time
from datetime import datetime
from inventorhatmini import InventorHATMini, SERVO_1, NUM_LEDS
from ioexpander import IN  # or IN_PU if a pull-up is wanted


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.leds = self.board.leds
        self.servo = self.board.servos[servo_id]
        self.input_mode = IN
        self.num_leds = NUM_LEDS


def detect_motion(timeout=5):
    InventorHATCoreInit = InventorHATCore()
    InventorHATCoreInit.board.gpio_pin_mode(0, InventorHATCoreInit.input_mode)

    start_time = time()
    while time() - start_time < timeout:
        if InventorHATCoreInit.board.gpio_pin_value(0):
            print(f"{datetime.now()}: DETECTED")
            return "DETECTED"
        sleep(0.1)  # Sleep a short duration before checking again

    return "NOT DETECTED"


def test_motion_detection(num_tests=5):
    print("Starting system warm-up. Please wait...")
    sleep(15)  # Warm-up period of 15 seconds

    passed_tests = 0
    for i in range(num_tests):
        print(f"\nTest {i + 1}/{num_tests}")
        print("Please wave your hand in front of the microwave sensor...")
        result = detect_motion()
        if result == "DETECTED":
            print("Test PASSED!")
            passed_tests += 1
        else:
            print("Test FAILED!")
        sleep(1)  # Allow a brief pause before the next test
    print(f"\n{passed_tests} out of {num_tests} tests passed!")


if __name__ == "__main__":
    test_motion_detection()
