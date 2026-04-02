import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOGIN_URL = "http://10.65.8.254/pams/front/login.do"


class PamsTask1Steps(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.set_capability("pageLoadStrategy", "eager")
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def _click_login_button_by_class(self, class_names):
        # 使用 CLASS_NAME 先找到候选元素，再筛选可点击按钮。
        for class_name in class_names:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            for el in elements:
                if el.tag_name.lower() == "button" and el.is_displayed() and el.is_enabled():
                    el.click()
                    return
        raise NoSuchElementException(f"未通过 CLASS_NAME 找到登录按钮: {class_names}")

    def test_task1_flow(self):
        driver = self.driver

        # 2) 打开网址。
        driver.get(LOGIN_URL)
        # 3) 浏览器窗口最大化。
        driver.maximize_window()

        # 4) NAME 定位用户名并输入 student。
        username_input = self.wait.until(EC.presence_of_element_located((By.NAME, "loginName")))
        username_input.clear()
        username_input.send_keys("student")

        # 5) ID 定位密码并输入 student。
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys("student")

        # 6) CLASS 定位登录按钮并点击。
        self._click_login_button_by_class(["blue-button", "btn-primary", "btn"])

        # 7) 强制等待 6 秒。
        time.sleep(6)

        # 8) LINK_TEXT 定位品牌按钮。
        brand_button = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "品牌")))
        self.assertTrue(brand_button.is_displayed(), "未定位到品牌按钮")

        # 9) 强制等待 6 秒。
        time.sleep(6)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
