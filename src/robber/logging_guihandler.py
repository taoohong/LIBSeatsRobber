import logging

from gui.logstream import LogStream

class GuiHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        LogStream.stderr().write('%s\n'%record)