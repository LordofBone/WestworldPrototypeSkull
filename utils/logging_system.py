from config.logging_config import log_level
import logging


class LockedLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._locked = False

    def setLevel(self, level):
        if self._locked:
            print(
                f"Logger level is locked at {logging.getLevelName(self.level)}. Ignoring attempt to set to {logging.getLevelName(level)}.")
            return
        print("locked")
        super().setLevel(level)
        self._locked = True


def get_locked_root_logger():
    if not isinstance(logging.root, LockedLogger):
        logging.root = LockedLogger(name="root", level=logging.WARNING)
        logging.Logger.root = logging.root
        logging.Logger.manager = logging.Manager(logging.Logger.root)
    return logging.root


# Use the custom function to get the root logger
logger = get_locked_root_logger()

# Now the rest of your initialization code
numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {log_level}')

logger.setLevel(numeric_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(numeric_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
