import logging
import re

SERVER_MSG = re.compile(r".*(?P<code>\d+) \d+$")
DOWNGRADE_CODES = {"200", "304"}


class ModifyLevelFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "django.server":
            message: str = record.getMessage()
            if match := SERVER_MSG.match(message):
                if match.group("code") in DOWNGRADE_CODES:
                    record.levelname = "DEBUG"
                    record.levelno = logging.DEBUG
        return True
