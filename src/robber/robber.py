import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import re, os, time, requests
from bs4 import BeautifulSoup
from robber.logging_guihandler import GuiHandler
import time

class Robber():
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.preferSeats = ['052', '054', '058', '060', '064', '070', 
                            '072', '066', '040', '046', '048', '042']
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter(
            '%(asctime)s-%(name)s-%(levelname)s-%(module)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fileHandler = logging.FileHandler(os.path.join(os.getcwd(), './log.txt') , \
            mode='w+', encoding='utf-8', delay=False)
        fileHandler.setFormatter(formatter)
        guiHandler = GuiHandler()
        guiHandler.setFormatter(formatter)
        self.logger.addHandler(guiHandler)
        self.logger.addHandler(fileHandler)
        self.logger.setLevel(logging.INFO)


    ############### 用户登录获取cookies ##################
    def getCookiesAndToken(self):
        self.logger.info("正在登录...")
        driver = webdriver.Chrome()
        driver.get("https://passport2.chaoxing.com/login?\
newversion=true&refer=http%3A%2F%2Foffice.chaoxing.com%2Ffront%2F\
third%2Fapps%2Fseat%2Flist%3FappId%3D1000%26deptIdEnc%3Db143e8d5830ee353")
        driver.find_element(by=By.XPATH, value='//*[@id="phone"]').clear()
        driver.find_element(by=By.XPATH, value='//*[@id="phone"]').send_keys(self.account) 
        driver.find_element(by=By.XPATH, value='//*[@id="pwd"]').clear()
        driver.find_element(by=By.XPATH, value='//*[@id="pwd"]').send_keys(self.password) 
        driver.find_element(by=By.XPATH, value='//*[@id="loginBtn"]').click()
        time.sleep(2)
        self.cookies = {}
        self.token = ''
        try:
            text = driver.find_element(by=By.ID, value='err-txt').text
            if not text == '':
                self.logger.error("登录失败")
                driver.close()
        except NoSuchElementException:
            self.logger.info("登录成功...")
            cookie = driver.get_cookies()
            for items in cookie:
                self.cookies[items.get("name")] = items.get("value")
            driver.find_element(by=By.XPATH, value='/html/body/div/ul[1]/li[1]/span').click()
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')
            driver.close()
            whole_info = soup.find_all("script")[24].text
            self.token = re.search("token: '(\w{32})", whole_info).group(1)
            self.logger.info("已获取token: " + self.token)
            
        

    ################### 获取座位信息 ###########################
    def _getSeatsList(self, roomid, date):
        seats_url = 'http://office.chaoxing.com/data/apps/seat/seatgrid/roomid?roomId=' + roomid
        switch_url = 'http://office.chaoxing.com/data/apps/seat/room/info/switch?id=' + roomid \
                        + '&toDay=' + date
        uesd_seats_url = 'http://office.chaoxing.com/data/apps/seat/getusedseatnums?roomId=' + roomid \
                            + '&startTime=08:00&endTime=17:30&day=' + date
        seats_list = []
        ret = requests.get(seats_url, cookies=self.cookies)
        seats_list = ret.json().get("data").get("seatDatas")
        ret = requests.get(switch_url, cookies=self.cookies)
        switch_list = ret.json().get("data").get("seatAttributes")
        unusable_list = []
        for item in switch_list:
            unusable_list.append(item["seatNum"])
        ret = requests.get(uesd_seats_url, cookies=self.cookies)
        used_list = ret.json().get("data").get("seatNums")
        seats_list = list(map(lambda x:x["seatNum"], list(filter(lambda x: x["seatNum"] not in used_list \
            and x["seatNum"] not in unusable_list, seats_list))))
        self.logger.info("已获取" + roomid + "房间可预约座位列表！还剩" + str(len(seats_list)) + "个座位")
        return seats_list


    def _refreshSeatsList(self, seats_list, roomid, date):
        uesd_seats_url = 'http://office.chaoxing.com/data/apps/seat/getusedseatnums?roomId=' + roomid \
                            + '&startTime=08:00&endTime=17:30&day=' + date
        ret = requests.get(uesd_seats_url, cookies=self.cookies)
        used_list = ret.json().get("data").get("seatNums")
        seats_list = list(filter(lambda x: x not in used_list, seats_list))
        self.logger.info("已刷新" + roomid + "房间可预约座位列表！还剩" + str(len(seats_list)) + "个座位")
        return seats_list


    ################### 预定一个座位 ###########################
    def orderSeat(self, roomid, seatNum, date):
        if self.token =='' or len(self.cookies) == 0:
            return [seatNum, date, 0]
        submit_url = 'http://office.chaoxing.com/data/apps/seat/submit?' \
            + 'roomId='+ roomid \
            + '&startTime=08:00' \
            + '&endTime=17:30' \
            + '&day='+ date \
            + '&seatNum='+ seatNum \
            + '&captcha=' \
            + '&token='+ self.token
        try:
            ret = requests.get(url=submit_url, cookies=self.cookies)
            success = ret.json().get('success')
            # data = ret.json().get("data")
            if success:
                return [seatNum, date, 1]
        except BaseException as e:
            if ret.status_code == 404:
                self.logger.error("页面不存在")
            else:
                self.logger.error("请求失败，正在重新尝试...")
        return [seatNum, date, 0]



    ################### 预约一楼座位 7827 ###########################
    def orderFirstFloor(self, date):
        seats_list = self._getSeatsList('7827', date)
        while True:
            if len(seats_list) == 0:
                return ['', date, 0]
            for preferSeat in self.preferSeats:
                if preferSeat in seats_list:
                    ret = self.orderSeat('7827', preferSeat, date)
                    if ret[2] == 1:
                        self.logger.info("优先座位预约成功！一楼座位：" + ret[0] + "，时间：" + ret[1])
                        return ret
                    else:
                        self.logger.info("优先座位预约失败")
                        self._refreshSeatsList(seats_list, '7827', date)
                        if len(seats_list) == 0:
                            return ['', date, 0]
            for others in seats_list:
                ret =  self.orderSeat('7827', others, date)
                if ret[2] == 1:
                    self.logger.info("非优先座位预约成功！一楼座位：" + ret[0] + "时间：" + ret[1])
                    return ret
                else:
                    self.logger.info("普通座位预约失败")
                    self._refreshSeatsList(seats_list, '7827', date)
                    if len(seats_list) == 0:
                        return ['', date, 0]
        


    ################### 预约三楼座位 7826 ###########################
    def orderThirdFloor(self, date):
        seats_list = self._getSeatsList('7826', date) 
        while True:
            if len(seats_list) == 0:
                return ['', date, 0]
            for others in seats_list:
                ret =  self.orderSeat('7826', others, date)
                if ret[2] == 1:
                    self.logger.info("预约成功！三楼座位：" + ret[0] + "时间：" + ret[1])
                    return ret
                else:
                    seats_list = self._refreshSeatsList(seats_list, '7826', date)
                    if len(seats_list) == 0:
                        return ['', date, 0]  



    ############################## 开始预约 #############################
    def startOrdering(self, date):
        if self.token == '' or len(self.cookies) == 0:
            raise RuntimeError("先登录")
        self.logger.info("正在预约一楼...")
        ret = self.orderFirstFloor(date)
        if ret[2] == 1:
            return ret
        self.logger.info("一楼已无空座!正在预约三楼...")
        ret = self.orderThirdFloor(date)
        if  ret[2] == 1:
            return ret
        self.logger.info("预约失败，已无空座")
