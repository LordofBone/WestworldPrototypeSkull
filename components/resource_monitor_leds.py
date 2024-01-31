import logging
import threading
import time

import psutil

from hardware.inventor_hat_controller import InventorHATCoreInit

logger = logging.getLogger(__name__)


class LedResourceMonitor:
    UPDATES = 50  # How many times the LEDs will be updated per second
    UPDATE_RATE = 1 / UPDATES
    AUTO_SHOW = False  # Update all LEDs at once after they have all been set
    INTERPOLATION_SPEED = 0.1  # Speed of interpolation (higher is faster)

    def __init__(self):
        self.current_mem_percentage = 0.0
        self.current_cpu_percentage = 0.0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.update_leds)

        logger.debug("Initialized")

    def sleep_until(self, end_time):
        time_to_sleep = end_time - time.monotonic()
        if time_to_sleep > 0.0:
            time.sleep(time_to_sleep)

    def update_leds(self):
        logger.debug("LED update thread started.")
        while not self.stop_event.is_set():
            start_time = time.monotonic()

            mem_info = psutil.virtual_memory()
            target_mem_percentage = mem_info.percent / 100.0
            self.current_mem_percentage += (
                                                   target_mem_percentage - self.current_mem_percentage) * self.INTERPOLATION_SPEED

            target_cpu_percentage = psutil.cpu_percent(interval=0.1) / 100.0
            self.current_cpu_percentage += (
                                                   target_cpu_percentage - self.current_cpu_percentage) * self.INTERPOLATION_SPEED

            hue = 0.33 * (1.0 - self.current_cpu_percentage)

            for i in range(InventorHATCoreInit.num_leds):
                if float(i) / InventorHATCoreInit.num_leds <= self.current_mem_percentage:
                    InventorHATCoreInit.leds.set_hsv(i, hue, 1.0, self.current_mem_percentage, show=self.AUTO_SHOW)
                else:
                    InventorHATCoreInit.leds.set_hsv(i, 0, 0, 0)

            if not self.AUTO_SHOW:
                InventorHATCoreInit.leds.show()

            self.sleep_until(start_time + self.UPDATE_RATE)

    def start(self):
        self.thread.start()
        logger.debug("LED Resource Monitor started.")

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        InventorHATCoreInit.leds.clear()
        logger.debug("LED Resource Monitor stopped.")
