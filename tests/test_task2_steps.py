import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGIN_URL = "http://10.65.8.254/pams/front/login.do"


def resolve_screenshot_dir():
    # 题目要求 E 盘 test 文件夹；非 Windows 环境下回退到仓库 screenshots 目录。
    if os.name == "nt":
        target = r"E:\test"
    else:
        target = os.path.join(BASE_DIR, "..", "screenshots", "E_test")
    os.makedirs(target, exist_ok=True)
    return target


class PamsTask2Steps(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.set_capability("pageLoadStrategy", "eager")
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def _find_username_input_by_class_name(self):
        # 仅使用 CLASS_NAME 进行定位，兼容常见登录输入框样式类名。
        candidate_classes = ["form-control", "inputxt", "text", "input"]
        for class_name in candidate_classes:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            for el in elements:
                if el.tag_name.lower() != "input" or not el.is_displayed():
                    continue
                element_type = (el.get_attribute("type") or "").lower()
                if element_type in {"hidden", "password", "checkbox", "radio", "submit", "button"}:
                    continue
                return el
        raise NoSuchElementException("未通过 CLASS_NAME 找到用户名输入框")

    def _click_brand_by_css_selector(self):
        # 使用 CSS_SELECTOR 先抓取所有链接，再筛选文本为“品牌”的菜单。
        brand_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
        for link in brand_links:
            if (link.text or "").strip() == "品牌" and link.is_displayed() and link.is_enabled():
                link.click()
                return
        raise NoSuchElementException("未通过 CSS_SELECTOR 找到品牌按钮")

    def test_task2_flow(self):
        driver = self.driver

        # 11) 打开网址。
        driver.get(LOGIN_URL)

        # 12) CLASS_NAME 定位用户名并输入 student。
        username_input = self._find_username_input_by_class_name()
        username_input.clear()
        username_input.send_keys("student")

        # 13) ID 定位密码并输入 student。
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys("student")

        # 14) XPATH 定位登录按钮并点击。
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'blue-button')]"))
        )
        login_button.click()

        # 15) CSS_SELECTOR 定位品牌按钮并点击。
        self.wait.until(EC.url_contains("index"))
        self._click_brand_by_css_selector()

        # 16) 点击页面中的新增按钮。
        add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".yellow")))
        add_button.click()

        # 17) 强制等待 2 秒。
        time.sleep(2)

        # 18) 截图保存到 E:\test（Windows）或回退目录（Linux/macOS）。
        screenshot_dir = resolve_screenshot_dir()
        ts = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshot_dir, f"task2_{ts}.png")
        saved = driver.get_screenshot_as_file(screenshot_path)
        self.assertTrue(saved, "截图保存失败")
        self.assertTrue(os.path.exists(screenshot_path), "截图文件不存在")
        print(f"截图保存路径: {screenshot_path}")

        # 19) 强制等待 2 秒。
        time.sleep(2)

        # 20) quit 关闭浏览器。
        driver.quit()
        self.driver = None

    def tearDown(self):
        if self.driver is not None:
            self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
