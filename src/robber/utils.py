import datetime, time

################### 获取时间戳 ###########################
def getToday():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def getTodayReadyTime():
    return getToday() + " 17:59:52"


def getTomorrow():
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


def getStartTime():
    start = int(time.mktime(time.strptime(getTomorrow() + ' ' + '08:00:00', '%Y-%m-%d %H:%M:%S')))
    return str(start) + '000'


def getEndTime():
    end = int(time.mktime(time.strptime(getTomorrow() + ' ' + '17:30:00', '%Y-%m-%d %H:%M:%S')))
    return str(end) + '000'

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def nowDelta(seconds=0):
    now = datetime.datetime.now()
    then = now + datetime.timedelta(seconds=seconds)
    return then.strftime("%Y-%m-%d %H:%M:%S")


def isLater(time, other):
    if time < other:
        return False
    else:
        return True
