import logging

from config.logging_config import log_level, log_format


class LockedLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._locked = False

    def setLevel(self, level):
        if self._locked:
            print(
                f"Logger level is locked at {logging.getLevelName(self.level)}. "
                f"Ignoring attempt to set to {logging.getLevelName(level)}.")
            return
        print(f"Logger level set and locked to {logging.getLevelName(level)}.")
        super().setLevel(level)
        self._locked = True


class LockedStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._formatter_locked = False

    def setFormatter(self, fmt):
        if self._formatter_locked:
            print("Formatter is locked. Ignoring attempt to change it.")
            return
        print("Formatter set and locked.")
        super().setFormatter(fmt)
        self._formatter_locked = True


def get_locked_root_logger():
    if not isinstance(logging.root, LockedLogger):
        logging.root = LockedLogger(name="root", level=logging.WARNING)
        logging.Logger.root = logging.root
        logging.Logger.manager = logging.Manager(logging.Logger.root)
    return logging.root


def activate_logging_system():
    # todo: find out why this works slightly differently when called as a function vs part of module import; some things
    # get missed in debug logging in some modules when called this way
    # Use the custom function to get the root logger
    logger = get_locked_root_logger()

    # Now the rest of your initialization code
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logger.setLevel(numeric_level)

    console_handler = LockedStreamHandler()
    console_handler.setLevel(numeric_level)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
