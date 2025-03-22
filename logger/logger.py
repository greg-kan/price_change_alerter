import logging
import sys


class Logger:
    def __init__(self, pname, plog_file, write_to_stdout=False, log_level=logging.INFO):
        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        file_handler = logging.FileHandler(plog_file)
        file_handler.setFormatter(log_formatter)

        self.vlogger = logging.getLogger(pname)
        self.vlogger.setLevel(log_level)
        self.vlogger.addHandler(file_handler)

        if write_to_stdout:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(log_formatter)
            self.vlogger.addHandler(stream_handler)

    def get(self):
        return self.vlogger
