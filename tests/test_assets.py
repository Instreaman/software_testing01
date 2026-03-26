import csv
import os
import time
import unittest

import ddt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "assets_data.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "..", "screenshots")


def get_test_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV file not found: {os.path.abspath(DATA_PATH)}")

    data_list = []
    with open(DATA_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row or all(not c.strip() for c in row):
                continue
            if len(row) != 5:
                raise ValueError(f"Invalid CSV row (must be 5 columns): {row}")
            data_list.append(row)

    if not data_list:
        raise ValueError("CSV has no valid test rows.")

    return data_list


@ddt.ddt
class PamsTest(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        self.driver.implicitly_wait(10)

    @ddt.data(*get_test_data())
    def test_add_asset_category(self, data):
        driver = self.driver
        wait = WebDriverWait(driver, 15)

        login_user, login_pwd, category_name, category_code, expected_alert = data

        try:
            driver.get("http://10.65.8.254/pams/front/login.do")
            driver.find_element(By.ID, "loginName").send_keys(login_user)
            driver.find_element(By.NAME, "password").send_keys(login_pwd)
            driver.find_element(By.TAG_NAME, "button").click()

            wait.until(EC.url_contains("index"))
            self.assertIn("front/index", driver.current_url, "登录失败")

            # Server requires 6-8 alnum chars for category code.
            base_code = "".join(ch for ch in category_code if ch.isalnum()).upper()
            now = int(time.time())
            code_suffix = str(now)[-2:]
            cn_tokens = "甲乙丙丁戊己庚辛壬癸"
            name_suffix = f"{cn_tokens[now % 10]}{cn_tokens[(now // 10) % 10]}"
            unique_code = f"{base_code[:6]}{code_suffix}"[:8]
            unique_name = f"{category_name}{name_suffix}"

            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "资产类别"))).click()
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "yellow"))).click()

            wait.until(EC.presence_of_element_located((By.NAME, "title"))).send_keys(unique_name)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#code"))).send_keys(unique_code)
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class,'modal')]//button[normalize-space()='保存']")
                )
            ).click()

            wait.until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            expected_norm = expected_alert.strip().rstrip("！!")
            actual_norm = alert_text.strip().rstrip("！!")
            self.assertEqual(
                expected_norm,
                actual_norm,
                f"断言失败：预期[{expected_alert}]，实际[{alert_text}]",
            )
            alert.accept()

            code_locator = (By.XPATH, f"//table//td[contains(., '{unique_code}')]")
            wait.until(EC.presence_of_element_located(code_locator))
            self.assertTrue(driver.find_element(*code_locator).is_displayed(), "页面二级断言失败：未找到新增编码")

        except Exception:
            # Avoid UnexpectedAlertPresentException when taking screenshot.
            try:
                driver.switch_to.alert.accept()
            except Exception:
                pass
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            screenshot = os.path.join(SCREENSHOT_DIR, f"test_add_asset_category_{ts}.png")
            try:
                driver.get_screenshot_as_file(screenshot)
            except Exception as screenshot_error:
                print(f"截图失败: {screenshot_error}")
            print(f"测试失败，截图已保存: {screenshot}")
            print(f"当前URL: {driver.current_url}")
            raise

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
