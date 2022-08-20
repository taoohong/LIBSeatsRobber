from multiprocessing.connection import wait
from time import sleep
from robber import Robber
from enum import Enum
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler import events
import utils as utils

class Schedule():

    def __init__(self, acc, pwd, date):
        super().__init__()
        self.acc = acc
        self.pwd = pwd
        self.date = date
    

    def run(self):
        self.robber = Robber(self.acc, self.pwd)
        if self.date == 'today':
            print("已开始今日补抢<br/>")
        elif self.date == 'tomorrow':
            print("已打开预抢，请保证程序一直处于运行中...<br/>")
        else:
            print("日期配置文件出错，请联系作者!!!!!!!!!!!!!<br/>")
        self.startSchedule(self.date)


    def startSchedule(self, date):
        self.scheduler = BlockingScheduler()
        if date == 'tomorrow':
            print("等待系统开启...")
            ready = utils.getTodayReadyTime()
            now = utils.now()
            if utils.isLater(now, ready):
                print("时间过了, 下次早点运行程序!!!!!!!!")
                return
            self.scheduler.add_job(self.robber.getCookiesAndToken, 'date', run_date=utils.getTodayReadyTime())
            self.scheduler.add_job(self.robber.startOrdering, 'date', run_date=utils.getToday() + ' 18:00:01', \
                    kwargs={'date': utils.getTomorrow()})
            # self.scheduler.add_job(self.robber.getCookiesAndToken, 'date', run_date=utils.nowDelta(2))
            # self.scheduler.add_job(self.robber.startOrdering, 'date', run_date=utils.nowDelta(8), \
            #         kwargs={'date': utils.getTomorrow()})
        else:
            print("17点之前每10分钟扫描一回，请勿关闭程序...")
            now = utils.now()
            end = utils.getToday() + ' 17:00:00'
            if not utils.isLater(now, end):
                print("时间过了, 下次早点运行程序!!!!!!!!!!!!")
                return
            self.scheduler.add_job(self.robber.getCookiesAndToken, 'interval', minutes=10, \
                start_date=utils.nowDelta(2), end_date=end)
            self.scheduler.add_job(self.robber.startOrdering, 'interval', minutes=10, \
                start_date=utils.nowDelta(8), end_date=end, kwargs={'date':utils.getToday()})
        self.scheduler.add_listener(self.eventHandler, events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED) 
        self.scheduler.add_listener(self.succesHandler, events.EVENT_JOB_EXECUTED)
        self.scheduler.start()


    def eventHandler(self, ev):
        self.scheduler.remove_listener(self.eventHandler)
        if ev.exception:
            print("出现错误!!!!!!!!!!!")
        else:
            print("你也不看看现在几点了!!!!!!!!!!!!")


    def succesHandler(self, ev):
        if ev.retval:
            if len(ev.retval) > 2 and ev.retval[2]:
                print("座位:"+ ev.retval[0] + " , 时间:" + ev.retval[1])
            else:
                print("预约失败")

class ScheException(Enum):
    EXCEPTION = 1,
    MISS = 2