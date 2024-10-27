from logging import getLogger
from typing import TypeVar

from django.conf import settings

logger = getLogger(__name__)


T = TypeVar("T")


def log_startup(get_response: T) -> T:
    logger.info(f"Started with ALLOWED_HOSTS={settings.ALLOWED_HOSTS}")
    logger.info(f"Template folder {settings.TEMPLATES[0]['DIRS']}")
    logger.debug(f"Debug works? {settings.DATABASES}")
    return get_response
