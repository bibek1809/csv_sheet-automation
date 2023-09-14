import logging
import os
from logging.handlers import RotatingFileHandler

from utils.Env import Env


class LoggerFactory:

    def __init__(self, env: Env):
        self.env = env
        self.loggers = {}

    def get_logger_configuration(self, logger_name):
        return {
            "name": logger_name,
            "level": self.env.get_or_default("logger." + logger_name + ".level",
                                             self.env.get_or_default("server.log.level", "INFO")),
            "handlers": self.env.get_or_default("logger." + logger_name + ".handlers", "console_handler").strip().split(
                ","),
            "formatter": self.env.get_or_default("logger." + logger_name + ".formatter",
                                                 "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "filepath": self.env.get_or_default("logger." + logger_name + ".filehandler.filepath", "/dev/null"),
            "max_bytes": int(self.env.get_or_default("logger." + logger_name + ".rolling.max_bytes", "40000")),
            "backupCount": int(self.env.get_or_default("logger." + logger_name + ".rolling.backupCount", "5242880")),
        }

    def __build_logger(self, logger_name):
        config = self.get_logger_configuration(logger_name=logger_name)
        # print(config)
        _logger = logging.getLogger(config["name"])
        _logger.setLevel(config["level"])
        for handler in config["handlers"]:
            # print(handler)
            if handler == "console_handler":
                stream = logging.StreamHandler()
                stream.setLevel(config["level"])
                stream.setFormatter(logging.Formatter(config["formatter"]))
                _logger.addHandler(stream)
                del stream
            elif handler == "file_handler":
                file_handler = logging.FileHandler(config["filepath"])
                file_handler.setLevel(config["level"])
                file_handler.setFormatter(logging.Formatter(config["formatter"]))
                _logger.addHandler(file_handler)
                del file_handler
            elif handler == "rolling_file_handler":
                rolling_handler = RotatingFileHandler(filename=config["filepath"], maxBytes=int(config["max_bytes"]),
                                                      backupCount=int(config["backupCount"]))
                rolling_handler.setLevel(config["level"])
                rolling_handler.setFormatter(logging.Formatter(config['formatter']))
                _logger.addHandler(rolling_handler)
                del rolling_handler
        return _logger

    def _get_logger(self, logger_name):
        if logger_name not in self.loggers:
            self.loggers[logger_name] = self.__build_logger(logger_name)
        return self.loggers[logger_name]

    __instance = None

    @classmethod
    def get_logger(cls, logger_name):
        if LoggerFactory.__instance is None:
            LoggerFactory.__instance = LoggerFactory(Env.instance())
        return LoggerFactory.__instance._get_logger(logger_name)
