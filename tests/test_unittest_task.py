import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FALLBACK_SCREENSHOT_DIR = os.path.join(BASE_DIR, "..", "screenshots")
WINDOWS_SCREENSHOT_DIR = r"E:\\test"
LOGIN_URL = "http://10.65.8.254/pams/front/login.do"
VISUAL_REACTION_DELAY = 0.6


def get_screenshot_dir():
    # 题目要求保存到 E 盘 test 目录；非 Windows 环境回落到仓库 screenshots 目录。
    if os.name == "nt" and os.path.exists("E:\\"):
        return WINDOWS_SCREENSHOT_DIR
    return FALLBACK_SCREENSHOT_DIR


class PamsUnittestTask(unittest.TestCase):
    def setUp(self):
        options = Options()
        # 与现有脚本保持一致：默认可视化运行，必要时可自行开启无头参数。
        # 采用 eager 页面加载策略，DOM 可交互后立即继续，减少肉眼等待时间。
        options.set_capability("pageLoadStrategy", "eager")
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.default_implicit_wait = 3
        self.driver.implicitly_wait(self.default_implicit_wait)
        self.wait = WebDriverWait(self.driver, 10)

    def _take_screenshot(self, prefix):
        screenshot_dir = get_screenshot_dir()
        os.makedirs(screenshot_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(screenshot_dir, f"{prefix}_{ts}.png")
        self.driver.get_screenshot_as_file(file_path)
        return file_path

    def _fast_click_link_text(self, link_text):
        # 快速路径：元素出现就用 JS 点击，减少 element_to_be_clickable 的等待时长。
        try:
            el = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located((By.LINK_TEXT, link_text))
            )
            self.driver.execute_script("arguments[0].click();", el)
            return
        except Exception:
            pass
        # 回退路径：仍保留常规可点击等待，保证稳定性。
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text))).click()

    def _find_login_inputs_by_class(self):
        # 使用 CLASS_NAME 复数查找用户名和密码输入框。
        candidate_classes = ["form-control", "inputxt", "text", "input"]
        for class_name in candidate_classes:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            inputs = []
            for el in elements:
                if el.tag_name.lower() != "input":
                    continue
                if not el.is_displayed():
                    continue
                el_type = (el.get_attribute("type") or "").lower()
                if el_type in {"hidden", "checkbox", "radio", "file", "submit", "button"}:
                    continue
                inputs.append(el)
            if len(inputs) >= 2:
                return inputs[0], inputs[1]
        raise NoSuchElementException("未通过 CLASS_NAME 复数定位到登录输入框")

    def _click_button_by_class_and_text(self, class_names, button_text):
        # 通过 CLASS_NAME 找到目标按钮，再按文案筛选，满足题目定位方式要求。
        for class_name in class_names:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            for el in elements:
                text = (el.text or "").strip()
                if button_text in text and el.is_displayed() and el.is_enabled():
                    el.click()
                    return
        raise NoSuchElementException(f"未通过 CLASS_NAME 定位到按钮: {button_text}")

    def _send_keys_by_id_candidates(self, id_candidates, value, field_name):
        # 避免逐个 find_element 叠加隐式等待：一次轮询匹配全部候选 ID。
        selector = ",".join(f"#{element_id}" for element_id in id_candidates)
        self.driver.implicitly_wait(0)
        try:
            deadline = time.time() + 3
            while time.time() < deadline:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    element_id = (el.get_attribute("id") or "").strip()
                    if element_id in id_candidates and el.is_displayed():
                        el.clear()
                        el.send_keys(value)
                        return element_id
                time.sleep(0.1)
        finally:
            self.driver.implicitly_wait(self.default_implicit_wait)
        raise NoSuchElementException(f"未通过 ID 定位到字段: {field_name}")

    def test_A(self):
        driver = self.driver
        try:
            # 进入登录页，按题目要求使用 ID/NAME/TAG_NAME 登录。
            driver.get(LOGIN_URL)
            self.wait.until(EC.presence_of_element_located((By.ID, "loginName"))).send_keys("student")
            self.wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("student")
            driver.find_element(By.TAG_NAME, "button").click()

            # 题目要求：执行截图并保存。
            screenshot_path = self._take_screenshot("test_A_login")
            self.assertTrue(os.path.exists(screenshot_path), "截图文件未生成")
            print(f"test_A 截图保存路径: {screenshot_path}")

        except Exception:
            failed_path = self._take_screenshot("test_A_failed")
            print(f"test_A 失败截图: {failed_path}")
            raise

    def test_B(self):
        driver = self.driver
        wait = self.wait
        try:
            # 进入登录页，按题目要求使用 CLASS_NAME 复数定位账号和密码输入框。
            driver.get(LOGIN_URL)
            username_input, password_input = self._find_login_inputs_by_class()
            username_input.clear()
            username_input.send_keys("student")
            password_input.clear()
            password_input.send_keys("student")

            # 通过 TAG_NAME 登录。
            driver.find_element(By.TAG_NAME, "button").click()
            wait.until(EC.url_contains("index"))

            # 通过 LINK_TEXT 点击“品牌”（快速路径）。
            self._fast_click_link_text("品牌")
            # 给肉眼一个短暂反应时间，避免流程快到看不清。
            time.sleep(VISUAL_REACTION_DELAY)

            # 通过 CLASS_NAME 点击“新增”。
            self._click_button_by_class_and_text(
                ["yellow", "btn", "btn-primary", "add", "button"],
                "新增",
            )

            # 通过 ID 输入品牌名称和品牌编码。
            now = int(time.time())
            cn_tokens = "甲乙丙丁戊己庚辛壬癸"
            suffix = f"{cn_tokens[now % 10]}{cn_tokens[(now // 10) % 10]}"
            brand_name = f"自动化品牌{suffix}"
            brand_code = f"BR{str(now)[-6:]}"
            self._send_keys_by_id_candidates(
                ["brandName", "name", "title"],
                brand_name,
                "品牌名称",
            )
            self._send_keys_by_id_candidates(
                ["brandCode", "code"],
                brand_code,
                "品牌编码",
            )

            # 通过 CLASS_NAME 点击“保存”。
            self._click_button_by_class_and_text(
                ["btn", "btn-primary", "green", "save", "button"],
                "保存",
            )

            # 若出现弹窗则接收，避免影响后续截图与关闭浏览器。
            try:
                WebDriverWait(driver, 4).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                print(f"test_B 弹窗信息: {alert.text}")
                alert.accept()
            except TimeoutException:
                pass

        except Exception:
            failed_path = self._take_screenshot("test_B_failed")
            print(f"test_B 失败截图: {failed_path}")
            raise

    def tearDown(self):
        # 与现有脚本一致：无论成功失败都释放浏览器进程。
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)