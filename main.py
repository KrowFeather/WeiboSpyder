import json
import os
import re
import time
import shutil
import urllib.request

import cv2
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from constants.account import MAIL_ACC, MAIL_PWD, PHONE, PHONE_PWD, PHONE_ACC, MAIL, HEADLESS, HEAD


def get_pos(template, block, driver):
    blockJpg = './resource/blockJpg.jpg'
    templateJpg = './resource/templateJpg.jpg'
    block = cv2.imread(block, 0)
    tp = cv2.imread(template, 0)
    cv2.imwrite(templateJpg, tp)
    cv2.imwrite(blockJpg, block)
    block = cv2.imread(blockJpg)
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite(blockJpg, block)
    block = cv2.imread(blockJpg)
    tp = cv2.imread(templateJpg)
    result = cv2.matchTemplate(block, tp, cv2.TM_CCOEFF_NORMED)
    mn_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(min_loc, max_loc)
    if min_loc[0] > max_loc[0]:
        y = min_loc[0]
    else:
        y = max_loc[0]

    if min_loc[1] > max_loc[1]:
        x = max_loc[1]
    else:
        x = min_loc[1]

    if x < 20:
        if min_loc[1] > max_loc[1]:
            x = min_loc[1]
        else:
            x = max_loc[1]

    cv2.rectangle(tp, (y, x), (y + 60, x + 60), (7, 249, 151), 2)
    print('X coordinate：%d' % x)
    print('Y coordinate：%d' % y)
    return y, tp


def get_tracks(dis):
    v = 0
    m = 0.3
    # 保存0.3内的位移
    tracks = []
    current = 0
    mid = dis * 4 / 5
    while current <= dis:
        if current < mid:
            a = 5
        else:
            a = -1
        v0 = v
        s = v0 * m + 0.5 * a * (m ** 2)
        current += s
        tracks.append(round(s))
        v = v0 + a * m
    return tracks


def autoSlider(browser):
    print('Get Slider...')
    time.sleep(2)
    captcha = browser.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[1]/div[2]/div/div/div[1]/div[2]")
    cap_block = browser.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/div[1]')
    s = captcha.get_attribute("style")
    s_b = cap_block.get_attribute("style")
    p = 'background-image: url\(\"(.*?)\"\);'
    captchaSrc = re.findall(p, s, re.S)[0]
    cap_blockSrc = re.findall(p, s_b, re.S)[0]
    urllib.request.urlretrieve(captchaSrc, './resource/captchaSlider.png')
    urllib.request.urlretrieve(cap_blockSrc, './resource/captchaSlider_block.png')
    print('OK: Slider Got')
    print('Get Position...')
    dis, _ = get_pos('./resource/captchaSlider.png', './resource/captchaSlider_block.png', browser)
    time.sleep(1)
    print('OK: position got, distance got')
    tracks = get_tracks(dis)
    tracks.append(-(sum(tracks) - dis))
    element = browser.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[1]/div[2]/div/div/div[2]/div/div[3]')
    ActionChains(browser).click_and_hold(on_element=element).perform()
    for track in tracks:
        ActionChains(browser).move_by_offset(xoffset=track, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(browser).release(on_element=element).perform()


def addOptions(type):
    if type == 1:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=old')
        return options
    else:
        return None


def login(type):
    print('Login...')
    if type == 1:
        browser = webdriver.Chrome(options=addOptions(HEADLESS))
        browser.get('https://mail.sina.com.cn/')
        time.sleep(2)
        acc_input = browser.find_element(By.ID, 'freename')
        acc_input.send_keys(MAIL_ACC)
        pwd_input = browser.find_element(By.ID, 'freepassword')
        pwd_input.send_keys(MAIL_PWD)
        time.sleep(1)
        loginBtn = browser.find_element(By.XPATH, "//a[@class='loginBtn']")
        loginBtn.click()
        time.sleep(2)
        print('Auto Sliding...')
        autoSlider(browser)
        time.sleep(6)
        print('OK: Auto Slide OK')
        browser.get('https://weibo.com')
        time.sleep(3)
        cookies = browser.get_cookies()
        with open('./resource/cookie.json', 'w') as f:
            f.write(json.dumps(cookies))
        print('OK:Login Success, Cookie Saved!')
    else:
        browser = webdriver.Chrome(options=addOptions(HEAD))
        browser.get('https://passport.weibo.com/sso/signin')
        time.sleep(2)
        el = browser.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/ul/li[2]/a')
        el.click()
        time.sleep(1)
        acc_input = browser.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/form/div[1]/input')
        acc_input.send_keys(PHONE_ACC)
        pwd_input = browser.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/form/div[2]/input')
        pwd_input.send_keys(PHONE_PWD)
        time.sleep(1)
        loginBtn = browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/button")
        loginBtn.click()
        time.sleep(25)
        browser.get('https://weibo.com')
        time.sleep(3)
        cookies = browser.get_cookies()
        with open('./resource/cookie.json', 'w') as f:
            f.write(json.dumps(cookies))
        print('OK: Login Success, Cookie Saved!')


def getHomeUrl(user_id):
    return f'https://weibo.com/u/{user_id}'


def getUserUrl(user_id):
    return f'https://weibo.com/ajax/profile/info?uid={user_id}'


def getFriendUrl(user_id):
    return f'https://weibo.com/ajax/friendships/friends?page=1&uid={user_id}'


def getFansUrl(user_id):
    return f'https://weibo.com/ajax/friendships/friends?relate=fans&page=1&uid={user_id}&type=all&newFollowerCount=0'


class WeiboSpyder:
    def __init__(self, user_id,option):
        self.user_id = user_id
        self.browser = webdriver.Chrome(options=addOptions(option))
        self.url = getUserUrl(user_id)
        self.friends_url = getFriendUrl(user_id)
        self.fans_url = getFansUrl(user_id)
        self.home_url = getHomeUrl(user_id)

    def getUserInfo(self):
        self.browser.get(self.url)
        time.sleep(3)
        el = self.browser.find_element(By.XPATH, '/html/body/pre')
        print(el.text)
        content = json.loads(el.text)
        with open(f'./results/{self.user_id}/{self.user_id}_info.txt', 'w', encoding='utf-8') as f:
            f.write(str(content['data']['user']))

    def getFriendInfo(self):
        self.browser.get(self.friends_url)
        with open('./resource/cookie.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                self.browser.add_cookie(cookie)
        time.sleep(2)
        self.browser.refresh()
        time.sleep(2)
        el = self.browser.find_element(By.XPATH, '/html/body/pre')
        content = json.loads(el.text)
        print(content)
        with open(f'./results/{self.user_id}/{self.user_id}_friends.txt', 'w', encoding='utf-8') as f:
            f.write(str(content['users']))

    def getFansInfo(self):
        login(PHONE)
        self.browser.get(self.fans_url)
        with open('./resource/cookie.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                self.browser.add_cookie(cookie)
        time.sleep(2)
        self.browser.refresh()
        time.sleep(2)
        el = self.browser.find_element(By.XPATH, '/html/body/pre')
        content = json.loads(el.text)
        print(content)
        with open(f'./results/{self.user_id}/{self.user_id}_fans.txt', 'w', encoding='utf-8') as f:
            f.write(str(content['users']))

    def getPrimeBlogs(self):
        self.browser.delete_all_cookies()
        self.browser.get(self.home_url)
        time.sleep(4)
        cur_top = 0
        st = set()
        while True:
            self.browser.execute_script("window.scrollBy(0,500)")
            time.sleep(3)
            els = self.browser.find_elements(By.CLASS_NAME, 'head-info_time_6sFQg')
            time.sleep(2)
            for el in els:
                try:
                    st.add(el.get_attribute('href').split('/')[-1])
                except Exception as e:
                    pass
            print(st)
            print('size:', len(st))
            check_height = self.browser.execute_script(
                "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
            if check_height == cur_top or len(st) >= 20:
                break
            cur_top = check_height
        l = list(st)
        mp = {'mid': l}
        with open(f'./results/{self.user_id}/primeblogs.json', 'w', encoding='utf-8') as f:
            json.dump(mp, f)
        print(st)
        time.sleep(2)

    def getPrimeBlogsInfo(self):
        pass

    def work(self):
        print('Get user info...')
        self.getUserInfo()
        print('OK')
        print('Get friend info...')
        self.getFriendInfo()
        print('OK')
        # print('get fans info...')
        # self.getFansInfo()
        print('Get prime blogs mids...')
        self.getPrimeBlogs()
        print('OK')
        print('Get prime blogs info...')
        self.getPrimeBlogsInfo()
        print('OK')



if __name__ == '__main__':
    login(MAIL)
    with open('./resource/users.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            lis = line.strip().split(' ')
            userid = lis[0]
            username = lis[1]
            print(userid, username)
            if os.path.exists(f'./results/{userid}'):
                shutil.rmtree(f'./results/{userid}')
            os.mkdir(f'./results/{userid}')
            weiboSpyder = WeiboSpyder(userid,HEADLESS)
            weiboSpyder.work()
