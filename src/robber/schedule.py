from multiprocessing.connection import wait
from PyQt5.QtCore import QObject, pyqtSignal
from robber.robber import Robber
from enum import Enum
from apscheduler.schedulers.qt import QtScheduler
from apscheduler import events
import robber.utils as utils
import datetime,time

class Schedule(QObject):
    finished = pyqtSignal(str)
    processing = pyqtSignal(str)
    exception = pyqtSignal(object, str)


    def __init__(self, acc, pwd, date):
        super().__init__()
        self.acc = acc
        self.pwd = pwd
        self.date = date
    

    def run(self):
        self.robber = Robber(self.acc, self.pwd)
        if self.date == 'today':
            self.processing.emit("已开始今日补抢<br/>")
        elif self.date == 'tomorrow':
            self.processing.emit("已打开预抢，请保证程序一直处于运行中...<br/>")
        else:
            self.processing.emit("日期配置文件出错，请联系作者!<br/>")
        self.startSchedule(self.date)


    def startSchedule(self, date):
        self.scheduler = QtScheduler()
        if date == 'tomorrow':
            self.processing.emit("等待系统开启...")
            self.scheduler.add_job(self.robber.getCookiesAndToken, 'date', run_date=utils.getTodayReadyTime())
            self.scheduler.add_job(self.robber.startOrdering, 'date', run_date=utils.getToday() + ' 18:00:01', \
                    kwargs={'date': utils.getTomorrow()})
        else:
            self.processing.emit("17点之前每10分钟扫描一回，请勿关闭程序...")
            now = utils.now()
            end = utils.getToday() + ' 17:00:00'
            if utils.isLater(now, end):
                self.exception.emit(ScheException.EXCEPTION, "时间过了")
                return
            self.scheduler.add_job(self.robber.getCookiesAndToken, 'interval', minutes=10, \
                start_date=now + datetime.timedelta(seconds=2), end_date=end)
            self.scheduler.add_job(self.robber.startOrdering, 'interval', minutes=10, \
                start_date=now + datetime.timedelta(seconds=8), end_date=end, kwargs={'date':utils.getToday()})
        self.scheduler.add_listener(self.eventHandler, events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED) 
        self.scheduler.add_listener(self.succesHandler, events.EVENT_JOB_EXECUTED)
        self.scheduler.start()


    def eventHandler(self, ev):
        self.scheduler.remove_listener(self.eventHandler)
        if ev.exception:
            self.exception.emit(ScheException.EXCEPTION, ev.traceback)
        else:
            self.exception.emit(ScheException.MISS, ev.traceback)


    def succesHandler(self, ev):
        if ev.retval:
            if len(ev.retval) > 2 and ev.retval[2]:
                self.finished.emit("座位:"+ev.retval[0] + " , 时间:" + ev.retval[1])
            else:
                self.finished.emit("预约失败")


class ScheException(Enum):
    EXCEPTION = 1,
    MISS = 2