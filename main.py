from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from setting import InfoUser, Config
from loguru import logger
import pyautogui
import random
import numpy as np
import base64
import cv2
import time

class PcJd:
    def __init__(self, user_info: InfoUser) -> None:
        self.driver = webdriver.Chrome()
        self.user_info = user_info
        self.config = Config()

    def download_img(self):
        """
        下载验证码背景图和小图
        """
        bigimg_b64 = self.driver.find_element(By.XPATH, '//*[@class="JDJRV-bigimg"]/img').get_attribute('src')
        bigimg_data = base64.b64decode(bigimg_b64.replace('data:image/png;base64,', ''))
        bigimg_array = np.frombuffer(bigimg_data, np.uint8)
        bigimg_img = cv2.imdecode(bigimg_array, cv2.COLOR_RGB2BGR)

        smallimg_b64 = self.driver.find_element(By.XPATH, '//*[@class="JDJRV-smallimg"]/img').get_attribute('src')
        smallimg_data = base64.b64decode(smallimg_b64.replace('data:image/png;base64,', ''))
        smallimg_array = np.frombuffer(smallimg_data, np.uint8)
        smallimg_img = cv2.imdecode(smallimg_array, cv2.COLOR_RGB2BGR)
        return bigimg_img, smallimg_img

    def get_distance(self, bigimg_img, smallimg_img):
        """
        处理验证码，得到滑块移动距离
        """
        # 灰度化
        bigimg_gray = cv2.cvtColor(bigimg_img, cv2.COLOR_BGR2GRAY)
        smallimg_gray = cv2.cvtColor(smallimg_img, cv2.COLOR_BGR2GRAY)

        # 自适应阈值化
        # bigimg_thresh = cv2.adaptiveThreshold(bigimg_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)
        # smallimg_thresh = cv2.adaptiveThreshold(smallimg_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)
        # cv2.imshow("bigimg_thresh", bigimg_thresh)
        # cv2.imshow("smallimg_thresh", smallimg_thresh)

        # 边缘检测
        # bigimg_canny = cv2.Canny(bigimg_thresh, 0, 500)
        # smallimg_canny = cv2.Canny(smallimg_thresh, 0, 500)
        # cv2.imshow("bigimg_canny", bigimg_canny)
        # cv2.imshow("smallimg_canny", smallimg_canny)

        # 模板匹配
        result = cv2.matchTemplate(bigimg_gray, smallimg_gray, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)

        # cv画图验证匹配结果正确率
        # startX, startY = minLoc
        # endX = startX + smallimg_img.shape[0]
        # endY = startY + smallimg_img.shape[1]

        # cv2.rectangle(bigimg_img, (startX, startY), (endX, endY), (255, 0, 0), 3)
        # cv2.circle(bigimg_img, (startX, startY), 2, (0, 0, 255), 4)
        # cv2.imwrite(f"{i}.png", bigimg_img)
        # cv2.imshow("Output", bigimg_img)
        # cv2.waitKey(0)
        
        # 移动距离对应到网页需要缩放(网页显示的图片和实际图片存在一定的比例差异)
        return minLoc[0] * (278.4 / 360.0)
    

    def slide(self, x):
        """
        通过pyautogui模拟鼠标滑动
        """
        WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@class="JDJRV-slide-inner JDJRV-slide-btn"]')))
        slide_btn = self.driver.find_element(By.XPATH, '//*[@class="JDJRV-slide-inner JDJRV-slide-btn"]')
        # TODO 网页元素位置映射到pyautogui会有一定缩放
        offset_x = slide_btn.location.get('x') * 1.30
        offset_y = slide_btn.location.get('y') * 1.75

        # 直接滑到目标位置--会很难通过验证(用来调试移动距离是否正确)
        # pyautogui.moveTo(offset_x,offset_y,duration=0.1 + random.uniform(0,0.1 + random.randint(1,100) / 100))
        # pyautogui.mouseDown()
        # pyautogui.moveTo(offset_x + x * 1.25, offset_y, duration=0.28)
        # pyautogui.mouseUp()

        # TODO 根据验证码原图计算的移动距离也需要调一下缩放
        x = x * 1.25

        # 模拟滑动
        pyautogui.moveTo(offset_x,offset_y,duration=0.1 + random.uniform(0,0.1 + random.randint(1,100) / 100))
        pyautogui.mouseDown()
        offset_y += random.randint(9,19)
        pyautogui.moveTo(offset_x + int(x * random.randint(15,25) / 20),offset_y,duration=0.28)
        offset_y += random.randint(-9,0)
        pyautogui.moveTo(offset_x + int(x * random.randint(17,23) / 20),offset_y,
                         duration=random.randint(20,31) / 100)
        offset_y += random.randint(0,8)
        pyautogui.moveTo(offset_x + int(x * random.randint(19,21) / 20),offset_y,
                         duration=random.randint(20,40) / 100)
        offset_y += random.randint(-3,3)
        pyautogui.moveTo(x + offset_x + random.randint(-3,3),offset_y,duration=0.5 + random.randint(-10,10) / 100)
        offset_y += random.randint(-2,2)
        pyautogui.moveTo(x + offset_x + random.randint(-2,2),offset_y,duration=0.5 + random.randint(-3,3) / 100)
        pyautogui.mouseUp()
        time.sleep(1)

        # 判断密码是否正确
        if '账号名与密码不匹配，请重新输入' in self.driver.page_source:
            logger.info("账号密码错误")
            return 1
        
        if '欢迎登录' not in self.driver.page_source:
            logger.info("登录成功")
            return 0
        return 2


    def login(self):
        # 进入登入页面
        self.driver.get(self.config.login_url)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.config.login_url))
        self.driver.maximize_window()
        
        # 点击账号登录
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="login-tab login-tab-r"]/a')))
        self.driver.find_element(By.XPATH, '//*[@class="login-tab login-tab-r"]/a').click()

        # 账号密码输入
        self.driver.find_element(By.ID, "loginname").send_keys(self.user_info.username)
        self.driver.find_element(By.ID, "nloginpwd").send_keys(self.user_info.password)

        # 点击登录
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "loginsubmit")))
        self.driver.find_element(By.ID, "loginsubmit").click()

        # 循环验证
        for i in range(10):
            logger.info(f"开始第{i + 1}次滑块")
            # 下载验证码图片
            bigimg_img, smallimg_img = self.download_img()

            # 计算滑块移动距离
            x = self.get_distance(bigimg_img, smallimg_img)

            # 滑动滑块
            slide_state = self.slide(x)
            if slide_state in (0, 1):
                break

            time.sleep(2)
        else:
            logger.info("滑块验证码失败")
            return

        time.sleep(10)
    
    def main(self):
        self.login()

if __name__ == "__main__":
    user_info = InfoUser(
        username="",
        password=""
    )
    p = PcJd(user_info)
    p.main()