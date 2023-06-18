import time
from threading import Thread
from inventorhatmini import InventorHATMini, SERVO_1


class JawController(Thread):
    def __init__(self, servo_id=SERVO_1, open_pulse_width=25, close_pulse_width=75):
        Thread.__init__(self)
        self.board = InventorHATMini(init_leds=False)
        self.s = self.board.servos[servo_id]
        self.keep_running = True
        self._open_pulse_width = open_pulse_width
        self._close_pulse_width = close_pulse_width

    def run(self):
        # Continuous running behavior can be added here if needed
        pass

    def stop(self):
        self.keep_running = False

    def set_pulse_width(self, pulse_width):
        """
        Set the pulse width directly.
        :param pulse_width: The pulse width in microseconds.
        """
        self.s.value(pulse_width)
        time.sleep(0.5)

    def open_jaw(self, pulse_width=None):
        pulse_width = pulse_width if pulse_width is not None else self._open_pulse_width
        self.set_pulse_width(pulse_width)
        print("Jaw opened")

    def close_jaw(self, pulse_width=None):
        pulse_width = pulse_width if pulse_width is not None else self._close_pulse_width
        self.set_pulse_width(pulse_width)
        print("Jaw closed")

    @property
    def open_pulse_width(self):
        return self._open_pulse_width

    @open_pulse_width.setter
    def open_pulse_width(self, value):
        self._open_pulse_width = value

    @property
    def close_pulse_width(self):
        return self._close_pulse_width

    @close_pulse_width.setter
    def close_pulse_width(self, value):
        self._close_pulse_width = value
