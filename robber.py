# @author: taosupr
# @function: Used to order a seat at the HuaiNing Library
# @warning:
# Propagation of this script is prohibited;
# This script is not intended for commercial use.

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import datetime
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

# 超星帐号
ACC = 'XXXXXXXXX'
# 超星密码
PWD = 'XXXXXXXXX'
cookies = {}
token = ""
              

############### 用户登录获取cookies ##################
def getCookiesAndToken():
    global cookies, token
    logging.info("正在登录...")
    driver = webdriver.Chrome()
    driver.get("https://passport2.chaoxing.com/login?\
newversion=true&refer=http%3A%2F%2Foffice.chaoxing.com%2Ffront%2F\
third%2Fapps%2Fseat%2Flist%3FappId%3D1000%26deptIdEnc%3Db143e8d5830ee353")
    driver.find_element(by=By.XPATH, value='//*[@id="phone"]').clear()
    driver.find_element(by=By.XPATH, value='//*[@id="phone"]').send_keys(ACC) 
    driver.find_element(by=By.XPATH, value='//*[@id="pwd"]').clear()
    driver.find_element(by=By.XPATH, value='//*[@id="pwd"]').send_keys(PWD) 
    driver.find_element(by=By.XPATH, value='//*[@id="loginBtn"]').click()
    time.sleep(1)
    cookie = driver.get_cookies()
    for items in cookie:
        cookies[items.get("name")] = items.get("value")
    logging.info("登录成功...")
    driver.find_element(by=By.XPATH, value='/html/body/div/ul[1]/li[1]/span').click()
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')
    driver.close()
    whole_info = soup.find_all("script")[24].text
    token = re.search("token: '(\w{32})", whole_info).group(1)
    logging.info("已获取token: " + token)
    


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


################### 获取座位信息 ###########################
def getSeatsList(roomid, date):
    seats_url = 'http://office.chaoxing.com/data/apps/seat/seatgrid/roomid?roomId=' + roomid
    switch_url = 'http://office.chaoxing.com/data/apps/seat/room/info/switch?id=' + roomid \
                     + '&toDay=' + date
    uesd_seats_url = 'http://office.chaoxing.com/data/apps/seat/getusedseatnums?roomId=' + roomid \
                        + '&startTime=08:00&endTime=17:30&day=' + date
    seats_list = []
    logging.info("正在尝试获取" + roomid + "房间的全部座位列表...")
    ret = requests.get(seats_url, cookies=cookies)
    seats_list = ret.json().get("data").get("seatDatas")
    logging.info("正在尝试获取" + roomid + "房间不可用或已预约座位列表...")
    ret = requests.get(switch_url, cookies=cookies)
    switch_list = ret.json().get("data").get("seatAttributes")
    unusable_list = []
    for item in switch_list:
        unusable_list.append(item["seatNum"])
    ret = requests.get(uesd_seats_url, cookies=cookies)
    used_list = ret.json().get("data").get("seatNums")
    logging.info("正在尝试获取" + roomid + "房间可预约座位列表...") 
    seats_list = list(map(lambda x:x["seatNum"], list(filter(lambda x: x["seatNum"] not in used_list and x["seatNum"] not in unusable_list, seats_list))))
    logging.info("已获取" + roomid + "房间可预约座位列表！")
    logging.info(seats_list)
    return seats_list


def refreshSeatsList(seats_list, roomid, date):
    uesd_seats_url = 'http://office.chaoxing.com/data/apps/seat/getusedseatnums?roomId=' + roomid \
                        + '&startTime=08:00&endTime=17:30&day=' + date
    ret = requests.get(uesd_seats_url, cookies=cookies)
    used_list = ret.json().get("data").get("seatNums")
    seats_list = list(filter(lambda x: x not in used_list, seats_list))
    logging.info("已刷新" + roomid + "房间可预约座位列表！")
    logging.info(seats_list)
    return seats_list


################### 预定一个座位 ###########################
def orderSeat(roomid, seatNum, date):
    submit_url = 'http://office.chaoxing.com/data/apps/seat/submit?' \
         + 'roomId='+ roomid \
         + '&startTime=08:00' \
         + '&endTime=17:30' \
         + '&day='+ date \
         + '&seatNum='+ seatNum \
         + '&captcha=' \
         + '&token='+ token
    try:
        ret = requests.get(url=submit_url, cookies=cookies)
        success = ret.json().get('success')
        # data = ret.json().get("data")
        if success:
            return [seatNum, date, 1]
    except BaseException as e:
        if ret.status_code == 404:
            logging.error("页面不存在")
        else:
            logging.error("请求失败，正在重新尝试...")
    return ['', '', 0]



################### 预约一楼座位 7827 ###########################
preferSeats = ['052', '054', '058', '060']
def orderFirstFloor(date):
    seats_list = getSeatsList('7827', date)
    while True:
        if len(seats_list) == 0:
            return 0
        for preferSeat in preferSeats:
            if preferSeat in seats_list:
                ret =  orderSeat('7827', preferSeat, date)
                if ret[2] == 1:
                    logging.info("优先座位预约成功！一楼座位：" + ret[0] + "，时间：" + ret[1])
                    return 1
                else:
                    refreshSeatsList(seats_list, '7827', date)
                    if len(seats_list) == 0:
                        return 0
        for others in seats_list:
            ret =  orderSeat('7827', others, date)
            if ret[2] == 1:
                logging.info("非优先座位预约成功！一楼座位：" + ret[0] + "时间：" + ret[1])
                return 1
            else:
                refreshSeatsList(seats_list, '7827', date)
                if len(seats_list) == 0:
                    return 0
    


################### 预约三楼座位 7826 ###########################
def orderThirdFloor(date):
    seats_list = getSeatsList('7826', date) 
    while True:
        if len(seats_list) == 0:
            return 0
        for others in seats_list:
            ret =  orderSeat('7826', others, date)
            if ret[2] == 1:
                logging.info("预约成功！三楼座位：" + ret[0] + "时间：" + ret[1])
                return 1
            else:
                seats_list = refreshSeatsList(seats_list, '7826', date)
                if len(seats_list) == 0:
                    return 0  


############################## 开始预约 #############################
def startOrdering():
    logging.info("正在预约一楼...")
    date = getToday()
    if orderFirstFloor(date) == 1:
        return
    logging.info("一楼已无空座!正在预约三楼...")
    if orderThirdFloor(date) == 1:
        return 
    logging.info("预约失败，已无空座")
            
    
 
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(module)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S ',
                    level=logging.INFO)
    logging.info("等待系统开启...")
    scheduler = BlockingScheduler()
    scheduler.add_job(getCookiesAndToken, 'date', run_date=getTodayReadyTime())
    scheduler.add_job(startOrdering, 'date', run_date=getToday() + ' 18:00:00')
    scheduler.start()

    