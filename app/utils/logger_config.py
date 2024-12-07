from loguru import logger
from notifiers.logging import NotificationHandler

from app.settings import APP_CONFIG

file_path_log = "log.log"
logger.add(file_path_log, level="CRITICAL", rotation="10 MB")

TG_HANDLER = NotificationHandler("telegram", defaults=APP_CONFIG.tg.dict())
logger.add(TG_HANDLER, level="ERROR")
