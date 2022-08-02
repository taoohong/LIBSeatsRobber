import datetime, time

################### 获取时间戳 ###########################
def getToday():
    today = datetime.datetime.now()
    month = str(today.month)
    day = str(today.day)
    if today.month < 10:
        month = '0' + month
    if today.day < 10:
        day = '0' + day
    return str(today.year) + '-' + month + '-' + day

def getTodayReadyTime():
    return getToday() + " 17:59:55"

def getTomorrow():
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    month = str(tomorrow.month)
    day = str(tomorrow.day)
    if tomorrow.month < 10:
        month = '0' + month
    if tomorrow.day < 10:
        day = '0' + day
    return str(tomorrow.year) + '-' + month + '-' + day


def getStartTime():
    start = int(time.mktime(time.strptime(getTomorrow() + ' ' + '08:00:00', '%Y-%m-%d %H:%M:%S')))
    return str(start) + '000'


def getEndTime():
    end = int(time.mktime(time.strptime(getTomorrow() + ' ' + '17:30:00', '%Y-%m-%d %H:%M:%S')))
    return str(end) + '000'

