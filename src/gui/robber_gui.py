import sys, os
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QApplication, QWidget, QLabel, QDesktopWidget,
                             QTextBrowser, QPushButton, QGroupBox, QRadioButton, QMessageBox)
from PyQt5.QtGui import QIcon,QFont
from gui.login_dialog import LoginDialog
from gui.logstream import LogStream
from robber.config import Config
from robber.schedule import Schedule, ScheException


class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.initUI()

    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    
    def initUI(self):
        self.warnning = QLabel('author: taosupr\nfunction: Used to order'+\
        ' a seat at the \nHuaiNing Library \nwarning: Propagation of this \nscript is prohibited;' + \
        'This script is not \nintended for commercial use.')
        self.warnning.setStyleSheet("color:blue;")
        self.warnning.setFont(QFont('宋体',12, QFont.Bold))
        self.warnning.setFixedSize(450, 180)
        
        self.browser = QTextBrowser(self)

        self.startButt = QPushButton("开始预约")
        self.startButt.clicked.connect(self.start)

        self.forTodayCheckBox = QRadioButton("今日补抢", self)
        self.forTomorrowCheckBox = QRadioButton("明日预抢", self)
        self.forTomorrowCheckBox.setChecked(True)
        self.forTodayCheckBox.toggled.connect(lambda: self.dateChanged(self.forTodayCheckBox))
        self.forTomorrowCheckBox.toggled.connect(lambda: self.dateChanged(self.forTomorrowCheckBox))

        self.groupBox = QGroupBox("选择抢座日期")
        self.groupBox.setFlat(True)
        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(self.forTodayCheckBox)
        groupBoxLayout.addWidget(self.forTomorrowCheckBox)
        self.groupBox.setLayout(groupBoxLayout)

        LogStream.stdout().messageWritten.connect(self.browser.append)
        LogStream.stderr().messageWritten.connect(self.browser.append)

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.warnning)
        topLayout.addWidget(self.groupBox)
        topLayout.addWidget(self.startButt)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(self.browser)
        
        self.setLayout(mainLayout)
        # use absolute path for exe packaging
        self.setWindowIcon(QIcon('./icon.ico'))
        self.resize(1000, 600)
        self._center()
        self.setWindowTitle('怀宁图书馆恶霸小叮当')
        self.show()
        self.showLoginDialog()

    
    def dateChanged(self, btn):
        if btn.text() == "今日补抢":
            if btn.isChecked() == True:
                self.config.date = 'today'
        elif btn.text() == "明日预抢":
            if btn.isChecked() == True:
                self.config.date = 'tomorrow'


    def processLoginCancel(self, result):
        self.login.close()
        self.close()


    def processLogin(self, account, password):
        self.browser.append('您已登录，本软件不会保存您的账号密码<br/>')
        self.account = account
        self.password = password


    def start(self):
        self.startButt.setDisabled(True)
        self.worker = Schedule(self.account, self.password, self.config.date)
        self.wthread = QThread()
        self.worker.moveToThread(self.wthread)
        self.wthread.started.connect(self.worker.run)
        self.worker.finished[str].connect(self.wthread.quit)
        self.worker.finished[str].connect(self.workFinished)
        self.worker.finished[str].connect(self.worker.deleteLater)
        self.worker.processing[str].connect(self.refreshInfo)
        self.worker.exception[object, str].connect(self.exceptionHandler)
        self.wthread.finished.connect(self.wthread.deleteLater)
        self.wthread.start()


    def workFinished(self, str):
        QMessageBox.information(self, '完成', str, QMessageBox.Yes)
        self.startButt.setDisabled(False)


    def showLoginDialog(self):
        self.login = LoginDialog()
        self.login.signal.cancel.connect(self.processLoginCancel)
        self.login.signal.login.connect(self.processLogin)


    def closeEvent(self, a0):
        self.login.close()
        return super().closeEvent(a0)
        

    def refreshInfo(self, str):
        self.browser.append(str)


    def exceptionHandler(self, type, str):
        if type == ScheException.EXCEPTION:
            QMessageBox.warning(self, "错误", str, QMessageBox.Yes)
        elif type == ScheException.MISS:
            QMessageBox.warning(self, "错误", "不看看现在几点吗，来不及了", QMessageBox.Yes)
        self.wthread.quit()
        self.showLoginDialog()
        self.startButt.setDisabled(False)


def main():
    app = QApplication(sys.argv)
    MainWin()
    sys.exit(app.exec_())