from time import sleep, time
from datetime import datetime
import unittest
from inventorhatmini import InventorHATMini, SERVO_1, NUM_LEDS
from ioexpander import IN  # or IN_PU if a pull-up is wanted


class InventorHATCore:
    def __init__(self, servo_id=SERVO_1):
        self.board = InventorHATMini(init_leds=True)
        self.leds = self.board.leds
        self.servo = self.board.servos[servo_id]
        self.input_mode = IN
        self.num_leds = NUM_LEDS


class EnhancedAudioJawSyncTest(unittest.TestCase):
    def setUp(self):
        self.InventorHATCoreInit = InventorHATCore()
        self.InventorHATCoreInit.board.gpio_pin_mode(0, self.InventorHATCoreInit.input_mode)

    def detect_motion(self, timeout=5):

        start_time = time()
        while time() - start_time < timeout:
            if self.InventorHATCoreInit.board.gpio_pin_value(0):
                print(f"{datetime.now()}: DETECTED")
                return "DETECTED"
            sleep(0.1)  # Sleep a short duration before checking again

        return "NOT DETECTED"

    def test_motion_detection(self, num_tests=5):
        print("Starting system warm-up. Please wait...")
        sleep(15)  # Warm-up period of 15 seconds

        passed_tests = 0
        for i in range(num_tests):
            print(f"\nTest {i + 1}/{num_tests}")
            print("Please wave your hand in front of the microwave sensor...")
            result = self.detect_motion()
            if result == "DETECTED":
                print("Test PASSED!")
                passed_tests += 1
            else:
                print("Test FAILED!")
            sleep(1)  # Allow a brief pause before the next test
        print(f"\n{passed_tests} out of {num_tests} tests passed!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
