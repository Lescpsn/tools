import os
import logging
from logging import handlers


class Logger:
    def __init__(self, root_path, log_name, **kwargs):
        """Logger for system and custom use
        Arguments:
            root_path: root path of your project
            log_name: name for log file
            interval: default 1
            backup_count: default 7
        """
        interval = kwargs.get('interval', 1)
        backup_cnt = kwargs.get('backup_count', 7)

        log_path = f'{root_path}/logs/{log_name}/{log_name}.log'
        log_dir_path = os.path.dirname(log_path)
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)

        self.__logger = logging.getLogger(log_name)
        self.__logger.setLevel(logging.INFO)

        if not self.__logger.handlers:
            formatter = logging.Formatter('%(asctime)s | %(levelname)s : %(message)s')
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            time_handler = handlers.TimedRotatingFileHandler(
                filename=log_path,
                when='MIDNIGHT',
                interval=interval,
                backupCount=backup_cnt,
                encoding='utf-8'
            )
            time_handler.setFormatter(formatter)
            self.__logger.addHandler(time_handler)
            self.__logger.addHandler(stream_handler)

    def info(self, msg):
        self.__logger.info(msg)

    def error(self, msg):
        self.__logger.error(msg)
