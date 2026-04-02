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
# 测试数据与截图目录都按仓库相对路径定位，避免运行目录差异导致找不到文件。
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "assets_data.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "..", "screenshots")


def get_test_data():
    # 启动前先校验 CSV 是否存在，失败时尽早报错。
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV file not found: {os.path.abspath(DATA_PATH)}")

    data_list = []
    with open(DATA_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        # 跳过表头，逐行读取测试样例。
        next(reader, None)
        for row in reader:
            # 忽略空行，避免脏数据影响参数化测试。
            if not row or all(not c.strip() for c in row):
                continue
            # 每行固定 5 列：用户名、密码、类别名、类别编码、预期弹窗。
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
        # 强制可视化运行，忽略 HEADLESS 环境变量。
        # 如需恢复自动化无头运行，将下方注释去掉。
        # headless_raw = os.getenv("HEADLESS", "1").strip().lower()
        # is_headless = headless_raw not in {"0", "false", "no", "off"}
        # if is_headless:
        #     options.add_argument("--headless")

        # 每条用例独立启动浏览器，避免前一条用例状态污染。
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)


    @ddt.data(*get_test_data())
    def test_add_asset_category(self, data):
        driver = self.driver
        wait = WebDriverWait(driver, 15)

        login_user, login_pwd, category_name, category_code, expected_alert = data

        try:
            # 1) 登录系统。
            driver.get("http://10.65.8.254/pams/front/login.do")
            time.sleep(1.5)
            driver.find_element(By.ID, "loginName").send_keys(login_user)
            time.sleep(1)
            driver.find_element(By.NAME, "password").send_keys(login_pwd)
            time.sleep(1)
            driver.find_element(By.TAG_NAME, "button").click()
            time.sleep(1.5)

            wait.until(EC.url_contains("index"))
            self.assertIn("front/index", driver.current_url, "登录失败")
            time.sleep(1)

            # 2) 组装唯一测试数据，避免重复创建时冲突。
            base_code = "".join(ch for ch in category_code if ch.isalnum()).upper()
            now = int(time.time())
            code_suffix = str(now)[-2:]
            cn_tokens = "甲乙丙丁戊己庚辛壬癸"
            name_suffix = f"{cn_tokens[now % 10]}{cn_tokens[(now // 10) % 10]}"
            unique_code = f"{base_code[:6]}{code_suffix}"[:8]
            unique_name = f"{category_name}{name_suffix}"
            time.sleep(0.8)

            # 3) 进入“资产类别”并打开新增弹窗。
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "资产类别"))).click()
            time.sleep(1.2)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "yellow"))).click()
            time.sleep(1.2)

            # 4) 填写表单并保存。
            wait.until(EC.presence_of_element_located((By.NAME, "title"))).send_keys(unique_name)
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#code"))).send_keys(unique_code)
            time.sleep(1)
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class,'modal')]//button[normalize-space()='保存']")
                )
            ).click()
            time.sleep(1.5)

            # 5) 一级断言：校验弹窗文本是否符合预期（容忍中英文叹号差异）。
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
            time.sleep(1)
            alert.accept()
            time.sleep(1)

            # 6) 二级断言：页面表格中应出现刚创建的唯一编码。
            code_locator = (By.XPATH, f"//table//td[contains(., '{unique_code}')]")
            wait.until(EC.presence_of_element_located(code_locator))
            self.assertTrue(driver.find_element(*code_locator).is_displayed(), "页面二级断言失败：未找到新增编码")
            time.sleep(1.2)

        except Exception:
            # Avoid UnexpectedAlertPresentException when taking screenshot.
            # 失败兜底：先尝试关闭弹窗，再截图并打印上下文，方便排查。
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
        # 无论成功失败都关闭浏览器，避免残留进程。
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
