import logging
import threading
import time

import psutil

from config.resource_monitor_config import led_brightness
from hardware.inventor_hat_controller import InventorHATCoreInit

logger = logging.getLogger(__name__)


class LedResourceMonitor:
    UPDATES = 50  # How many times the LEDs will be updated per second
    UPDATE_RATE = 1 / UPDATES
    AUTO_SHOW = False  # Update all LEDs at once after they have all been set
    INTERPOLATION_SPEED = 0.1  # Speed of interpolation (higher is faster)
    LED_BRIGHTNESS = led_brightness  # Default LED brightness (0.0 to 1.0)

    def __init__(self, brightness=1.0):
        self.current_mem_percentage = 0.0
        self.current_cpu_percentage = 0.0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.update_leds)
        self.set_brightness(brightness)  # Set the initial brightness

        logger.debug("Initialized")

    def set_brightness(self, brightness):
        """Set the brightness level for the LEDs."""
        self.LED_BRIGHTNESS = max(0.0, min(1.0, brightness))  # Clamp value between 0.0 and 1.0

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

            # todo: find out why the LED_BRIGHTNESS is not working on the inventor HAT
            for i in range(InventorHATCoreInit.num_leds):
                if float(i) / InventorHATCoreInit.num_leds <= self.current_mem_percentage:
                    InventorHATCoreInit.leds.set_hsv(i, hue, 1.0, self.LED_BRIGHTNESS * self.current_mem_percentage,
                                                     show=self.AUTO_SHOW)
                else:
                    InventorHATCoreInit.leds.set_hsv(i, 0, 0, 0, self.LED_BRIGHTNESS)

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
