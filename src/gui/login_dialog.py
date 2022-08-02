from PyQt5.QtWidgets import (QDialog, QLabel,QLineEdit,
                            QPushButton, QDesktopWidget, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon

class Communicate(QObject):
    login = pyqtSignal(str, str)
    cancel = pyqtSignal(bool)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.account = ''
        self.password = ''

    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        self.signal = Communicate()

        label1 = QLabel("账号: ", self)
        label2 = QLabel("密码: ", self)
        input1 = QLineEdit(self)
        input2 = QLineEdit(self)
        label1.move(30, 20)
        label2.move(30, 50)
        input1.move(160, 20)
        input2.move(160, 50)

        btn1 = QPushButton("确定", self)
        btn1.move(60, 100)

        btn2 = QPushButton("取消", self)
        btn2.move(180, 100)

        btn1.clicked[bool].connect(self.sendLoginButt)
        btn2.clicked[bool].connect(self.sendCencelButt)
        input1.textChanged.connect(self.setAccount)
        input2.textChanged.connect(self.setPassword)
        self.setWindowIcon(QIcon('D:\Programs\HuaiNingLibrary\icon.ico'))
        self.resize(350, 200)
        self._center()
        self.setWindowTitle('先登录')
        self.show()


    def closeEvent(self, e):
        self.signal.cancel.emit(True)

    def setAccount(self, account):
        self.account = account
    
    def setPassword(self, password):
        self.password = password

    def sendCencelButt(self, result):
        self.signal.cancel.emit(True)
    
    def sendLoginButt(self):
        if self.account == '':
            QMessageBox.warning(self, '警告', "你账号呢？", QMessageBox.Yes)
        elif self.password == '':
            QMessageBox.warning(self, '警告', "密码等着我给你输?", QMessageBox.Yes)
        else:
            self.signal.login.emit(self.account, self.password)
            self.hide()