from sys import stderr
from datetime import datetime
from typing import Literal
from loguru import logger

LoggerMode = Literal["debug", "info", "error", "success", "warning", "critical"]


class Logger:
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        logger_format = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
        self.logger.add(stderr, format=logger_format)
        date = datetime.today().date()
        self.logger.add(f'./files/logs/{date}.log', level="INFO", format=logger_format)

    def log_msg(self, wallet_name=None, network=None, class_name=None, action_name=None, msg=None,
                msg_type: LoggerMode = "info"):
        parts = []

        if wallet_name:
            parts.append(wallet_name)

        if network:
            parts.append(network)

        if class_name:
            parts.append(class_name)

        if action_name:
            parts.append(f'{action_name}')

        if msg:
            parts.append(msg)
            log = " | ".join(parts)

            if msg_type == "info":
                self.logger.info(log.strip())

            elif msg_type == "error":
                self.logger.error(log.strip())

            elif msg_type == "success":
                self.logger.success(log.strip())

            elif msg_type == "warning":
                self.logger.warning(log.strip())

            elif msg_type == "critical":
                self.logger.critical(log.strip())
