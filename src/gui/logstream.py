from PyQt5.QtCore import QObject, pyqtSignal
import sys

class LogStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(str)

    def flush( self ):
        pass

    def fileno( self ):
        return -1

    def write( self, msg ):
        if (not self.signalsBlocked()):
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if ( not LogStream._stdout ):
            LogStream._stdout = LogStream()
            sys.stdout = LogStream._stdout
        return LogStream._stdout

    @staticmethod
    def stderr():
        if ( not LogStream._stderr ):
            LogStream._stderr = LogStream()
            sys.stderr = LogStream._stderr
        return LogStream._stderr