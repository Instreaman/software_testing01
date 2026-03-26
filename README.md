# software_testing 文档汇总

本 README 由原始多个 Markdown 文档合并整理而成。

---

## 来源文件: 动态获取当前脚本的绝对路径目录.md

自动化测试项目实战规范 (2026 迁移版)

适用环境：Arch Linux | VSCode | Firefox (GeckoDriver v0.36.0)
1. 核心改进：工程化路径管理 (Robust Pathing)

为了防止在项目根目录、tests/ 目录甚至外部脚本调用时路径失效，代码中必须使用脚本锚点定位：
Python

import os

# 动态获取当前脚本的绝对路径目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 向上跳一级找到 data 目录，确保无论从哪启动都能精准定位
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "assets_data.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "..", "screenshots")

2. 自动化练习核心步骤 (精细适配版)

基于《3月26日自动化练习.txt》及 PPT 逻辑 ：
(1-8) 环境初始化

    驱动创建：使用 Firefox 。统一使用双横线参数：options.add_argument("--headless")。
    
    窗口控制：maximize_window() 及 set_window_size(1920, 1080) 。
    
    等待策略：
    
        隐式等待：driver.implicitly_wait(10) 负责全局元素加载 。
    
        显式等待：针对关键交互（如登录跳转、弹窗、保存按钮），引入 WebDriverWait 提高稳定性。

(9-20) 
元素定位与操作 

    登录：ID 为 loginName，Name 为 password，Tag 为 button 。
    
    导航：back() -> forward() -> refresh() 。
    
    新增资产：
    
        点击“新增”按钮 (Class Name 定位) 。
    
        输入“类别名称” (Name 定位) 。
    
        输入“类别编码” (CSS Selector 定位) 。
    
        点击“保存” (XPATH 定位：推荐 //button[text()='保存'] 或 //span[contains(text(),'保存')]/..) 。

(21-23) 双重断言策略 (Double-Check)

    一级断言 (Alert)：处理 JS 弹窗 。
    
        文案对齐：根据 PAMS 系统规范，expected_alert 应设置为 “保存成功” 或 “操作成功” 。数据驱动的 CSV 文件需与此保持绝对一致。
    
        操作：alert.accept() 。
    
    二级断言 (Page Level)：关闭弹窗后，在资产列表中通过 By.XPATH 或 By.CSS_SELECTOR 验证刚才新增的 category_code 是否出现在表格中。

3. 测试数据规范 (data/assets_data.csv)

必须确保 CSV 的 expect 字段与系统真实反馈丝毫不差。
login_user	login_pwd	category_name	category_code	expected_alert
student	student	戴尔显示器	DELL-2026	保存成功
student	student	机械键盘	KEY-99	保存成功
4. 测试报告选型 (Reporting)

由于 HTMLTestRunner 官方已多年不更新且在 Arch 环境下手动管理 .py 源码较麻烦，强烈建议使用现代化的 unittest-xml-reporting。
安装 (在虚拟环境下)
代码段

pip install unittest-xml-reporting

执行脚本 (test_runner.py)

在项目根目录下创建一个统一的入口，这样 Copilot Agent 就能帮你跑整套测试：
Python

import unittest
import xmlrunner

if __name__ == '__main__':
    # 自动搜索 tests 目录下的所有用例
    suite = unittest.TestLoader().discover('./tests', pattern='test_*.py')
    # 生成 JUnit 兼容的 XML 报告（可被 VSCode 插件读取）
    with open('reports/results.xml', 'wb') as output:
        xmlrunner.XMLTestRunner(output=output).run(suite)

5. 开发者生存指南：VSCode + Copilot 提效

在 Arch Linux 环境下，你可以这样“喂”给 Copilot Agent：

    Prompt 1 (生成代码)：
    
        @workspace 根据“3月26日自动化练习.txt”的内容，在 tests/下创建一个符合规范的test_assets.py`。
    
            路径必须基于 os.path.abspath(__file__) 动态拼接。
    
            浏览器使用 Firefox，参数为 --headless。
    
            断言 expected_alert 必须等于“保存成功”。
    
    Prompt 2 (二次断言)：
    
        在 test_one 方法的 alert.accept() 之后，增加一个显式等待，验证页面表格中是否出现了刚才新增的资产编码。
---

## 来源文件: 数据读取工具 [cite 375-385].md

1. 项目工程结构 (Project Structure)

为了确保路径引用稳定且符合规范，建议采用以下标准目录结构：
Plaintext

pams_automation/
├── .venv/                  # 虚拟环境 (Virtual Environment)
├── data/                   # 测试数据
│   └── assets_data.csv     # 资产数据文件
├── tests/                  # 测试用例脚本
│   └── test_assets.py      # 核心测试用例 [cite: 281]
├── reports/                # 测试报告存放处
├── screenshots/            # 失败截图存放处 
└── utils/                  # 工具类（如自定义等待、驱动初始化）

2. 数据定义：assets_data.csv

在 Linux 下，CSV 必须使用 UTF-8 编码以支持中文 。

列名规范与示例数据：
| login_user | login_pwd | category_name | category_code | expected_alert |
| :--------- | :-------- | :------------ | :------------ | :------------- |
| student    | student   | 办公设备      | OFF-001       | 新增成功       |
| student    | student   | 电子耗材      | ELE-002       | 新增成功       |
3. 环境校验与驱动兼容

在开始编写脚本前，需验证驱动与浏览器的协同状态：

    版本匹配：GeckoDriver v0.36.0 推荐配合 Firefox v124.0 及以上版本。
    
    验证命令：在 Fish shell 中执行以下命令确认路径已生效：
    代码段
    
    geckodriver --version
    
    路径设置：确保 geckodriver 已通过 sudo mv 放入 /usr/local/bin/ 并执行 chmod +x。

4. 核心脚本模板 (带显式等待与异常处理)

该模板整合了 显式等待 (WebDriverWait) 、异常截图 及 断言策略 。
Python

import unittest
import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ddt

# 数据读取工具 [cite: 375-385]
def get_test_data():
    data_list = []
    # Linux 环境务必指定 encoding="utf-8"
    with open('../data/assets_data.csv', 'r', encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader) # 跳过标题行 [cite: 382]
        for row in reader:
            data_list.append(row)
    return data_list

@ddt.ddt
class PamsTest(unittest.TestCase):
    def setUp(self):
        options = Options()
        # Headless 模式建议在 CI 环境或无桌面 Linux 开启
        # options.add_argument("-headless") 
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window() [cite: 157]
        self.driver.implicitly_wait(10) # 基础隐式等待 [cite: 148]

    @ddt.data(*get_test_data())
    def test_add_asset_category(self, data):
        driver = self.driver
        wait = WebDriverWait(driver, 15) # 显式等待对象 [cite: 150]
        
        try:
            # 1. 登录流程 [cite: 125]
            driver.get("http://10.65.8.254/pams/front/login.do")
            driver.find_element(By.ID, "loginName").send_keys(data[0]) [cite: 128]
            driver.find_element(By.NAME, "password").send_keys(data[1]) [cite: 129]
            driver.find_element(By.TAG_NAME, "button").click() [cite: 130]
    
            # 2. 登录断言：验证是否进入首页 (检查 URL 或欢迎元素)
            wait.until(EC.url_contains("index"))
            self.assertIn("front/index", driver.current_url, "登录失败！")
    
            # 3. 幂等性处理：利用时间戳生成编码避免重复报错
            unique_code = f"{data[3]}_{int(time.time())}"
    
            # 4. 新增操作 [cite: 1]
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "资产类别"))).click() [cite: 132]
            driver.find_element(By.CLASS_NAME, "yellow").click() [cite: 131]
            driver.find_element(By.NAME, "title").send_keys(data[2])
            driver.find_element(By.CSS_SELECTOR, "#code").send_keys(unique_code) [cite: 135]
            driver.find_element(By.XPATH, "//button[@type='submit']").click() [cite: 134]
    
            # 5. 弹窗断言 [cite: 208-212, 393]
            wait.until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            self.assertEqual(alert_text, data[4], f"断言失败：预期 {data[4]} 但实际为 {alert_text}")
            alert.accept()
    
        except Exception as e:
            # 异常处理：自动截图并保存 [cite: 236, 391]
            if not os.path.exists("../screenshots"): os.makedirs("../screenshots")
            file_path = f"../screenshots/error_{int(time.time())}.png"
            driver.get_screenshot_as_file(file_path)
            print(f"测试失败，截图已保存至: {file_path}")
            raise e
    
    def tearDown(self):
        self.driver.quit() [cite: 165]

if __name__ == "__main__":
    unittest.main()

5. 开发与执行规范
   元素定位优先级 (Stability Rules)

    优先使用 ID / Name：效率最高且最稳定 。

    CSS Selector 次之：处理复杂样式定位时的首选 。

    XPath 最后考虑：仅在处理动态 DOM 或需要向上遍历父节点时使用 。

执行命令汇总 (CLI Commands)

    单文件运行：
    Bash
    
    python3 tests/test_assets.py
    
    批量发现并执行 (unittest discover)：
    Bash
    
    python3 -m unittest discover -s tests -p "test_*.py" -v

6. 进阶：测试报告生成

为了满足“可提交项目”的需求，建议集成 HTMLTestRunner。
在 test_assets.py 的执行入口中添加：
Python

if __name__ == "__main__":
    import HTMLTestRunner # 需先下载该 .py 文件放入 utils
    with open('../reports/report.html', 'wb') as f:
        runner = HTMLTestRunner.HTMLTestRunner(stream=f, title='PAMS 自动化测试报告')
        unittest.main(testRunner=runner)
---

## 来源文件: 数据读取函数 (适应 Linux 路径).md

自动化测试项目规范：资产管理系统 (PAMS)

环境适配： Arch Linux | VSCode | Firefox (GeckoDriver) | Python 3.10+
一、 系统环境配置 (System Setup)

在 Arch Linux 上，为了避免 externally-managed-environment 错误，必须使用虚拟环境。
1. 依赖安装 (Dependencies)

    驱动 (GeckoDriver)：版本 v0.36.0-linux64 。

        放置路径：/usr/local/bin/ 并赋予 +x 权限。

    Python 包：在虚拟环境下安装 。
    Bash

    python -m venv .venv
    source .venv/bin/activate.fish  # Fish shell
    pip install selenium==4.4.3 ddt

    VSCode 插件：安装 Python 和 GitHub Copilot。

二、 自动化练习核心步骤 (23 Steps Spec)

基于《3月26日自动化练习.txt》，迁移至 Firefox 逻辑 ：
1. 初始化与登录

    (1-3) 导入：引入 webdriver, time, By 类 。

    (4-6) 浏览器控制：创建 Firefox 对象，执行 maximize_window() 及 set_window_size(width, height) 。

    (7-8) 访问与等待：发送 get 请求至 http://10.65.8.254/pams/front/login.do ，设置 隐式等待 (Implicit Wait) 10秒 。

    (9-11) 登录操作：

        ID 定位：输入框 loginName 输入 student 。
    
        NAME 定位：输入框 password 输入 student 。
    
        TAG_NAME 定位：定位 button 并 click() 。

2. 页面交互练习

    (12-14) 导航控制：执行 back() (后退)、forward() (前进)、refresh() (刷新) 。

    (15, 16) 链接定位：

        使用 Partial link text 定位“资产类别”并点击 。
    
        使用 Link text 再次定位“资产类别”验证 。

    (17-20) 元素操作：

        CLASSNAME 定位：点击“新增”按钮 。
    
        NAME 定位：输入“类别名称” 。
    
        CSS_SELECTOR 定位：输入“类别编码” 。
    
        XPATH 定位：点击“保存” 。

3. 弹窗与退出

    (21) Alert 处理：通过 switch_to.alert.accept() 点击确定弹窗 。

    (22-23) 扫尾：后退至欢迎页，执行 显示等待 (Explicit Sleep) 6s，随后 quit() 退出驱动 。

三、 测试框架与数据驱动 (Framework & ddt)

迁移 PPT 中的 Windows 路径至 Linux 规范。

1. Unittest 核心组件 

    TestCase：所有测试类必须继承 unittest.TestCase 。

    TestFixture：

        setUp()：初始化 Firefox、最大化窗口、设置隐式等待 。
    
        tearDown()：执行 driver.quit() 释放资源 。

2. ddt 数据驱动模型 

    装饰器：类使用 @ddt.ddt，测试方法使用 @ddt.data(*g) 。

    CSV 读取 (Linux 适配)：

        不要使用 C:\Users\... ，改为相对路径 ./data/abc.csv。
        
        使用 csv.reader 转换为流对象，通过 list.append(row) 封装数据 。

四、 迁移版代码模板 (Firefox + venv)

你可以直接让 Copilot Agent 参考此结构：
Python

import unittest
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import ddt

# 数据读取函数 (适应 Linux 路径)
def get_data():
    import csv
    with open('assets_data.csv', 'r') as f:
        reader = csv.reader(f)
        return [row for i, row in enumerate(reader) if i != 0]

@ddt.ddt
class PamsFirefoxTest(unittest.TestCase):
    def setUp(self):
        opts = Options()
        # opts.add_argument("--headless") # Linux 无界面环境建议开启
        self.driver = webdriver.Firefox(options=opts)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    @ddt.data(*get_data())
    def test_add_asset(self, data_row):
        driver = self.driver
        # ... 按文档第 1-23 步实现逻辑 ...
        # 断言示例 [cite: 391]
        # self.assertEqual(driver.switch_to.alert.text, data_row[2])
    
    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()

五、 效率提升建议 (Copilot Agent Tips)

    定位建议：如果你需要 Copilot 帮你写具体的 XPATH，直接将浏览器开发者工具中 Copy 的 HTML 元素粘贴进 VSCode Chat，输入：@workspace 基于这段 HTML，用 By.XPATH 补全第 20 步的代码。
    
    错误调试：在 Arch Linux 下遇到 GeckoDriver 权限问题，选中报错信息输入：/fix 解释这个权限报错并给出 chmod 修复命令。
    
    数据转换：如果你有现成的 Excel 数据，可以对 Copilot 说：帮我把这段文本数据转换成符合 ddt 要求、名为 assets_data.csv 的文件。

下一步建议：
如果你已经准备好了测试数据（CSV 文件内容），我可以帮你写出完整的、带异常处理（Try-Except）和断言（Assert）的自动化脚本。你想先处理哪一部分？
---

## 来源文件: PAMS_自动化测试规范_2026_合并版.md

# 自动化测试项目实战规范（PAMS｜2026 合并版）

适用环境：Arch Linux | VSCode | Firefox | GeckoDriver v0.36.0 | Python 3.10+

## 1. 目标与范围

本规范用于指导 PAMS 资产管理系统自动化测试，从环境搭建、数据驱动、脚本编写、断言策略到测试报告输出形成统一流程。  
目标：在 Linux 环境下实现可重复执行、可追踪结果、可扩展维护的自动化测试工程。

---

## 2. 环境准备（Linux 规范）

### 2.1 虚拟环境（必须）

为避免 `externally-managed-environment` 错误，必须使用虚拟环境。

```bash
python3 -m venv .venv
source .venv/bin/activate.fish   # Fish shell
# 或
source .venv/bin/activate        # Bash/Zsh
```

### 2.2 依赖安装

建议固定版本，避免环境漂移。

```bash
pip install selenium==4.4.3 ddt==1.6.0 unittest-xml-reporting==3.2.0
```

可选 `requirements.txt`：

```txt
selenium==4.4.3
ddt==1.6.0
unittest-xml-reporting==3.2.0
```

安装命令：

```bash
pip install -r requirements.txt
```

### 2.3 驱动与浏览器兼容

- GeckoDriver：`v0.36.0-linux64`
- 推荐 Firefox：`v124.0+`
- 驱动放置：`/usr/local/bin/geckodriver`
- 权限：`chmod +x /usr/local/bin/geckodriver`

验证：

```bash
geckodriver --version
```

---

## 3. 项目目录结构（标准）

```text
pams_automation/
├── .venv/
├── data/
│   └── assets_data.csv
├── tests/
│   └── test_assets.py
├── reports/
├── screenshots/
├── utils/
├── test_runner.py
└── requirements.txt
```

---

## 4. 数据文件规范（CSV）

文件：`data/assets_data.csv`  
编码：`UTF-8`  
建议读取参数：`encoding="utf-8", newline=""`

字段必须是 5 列：

1. `login_user`
2. `login_pwd`
3. `category_name`
4. `category_code`
5. `expected_alert`

示例：

```csv
login_user,login_pwd,category_name,category_code,expected_alert
student,student,戴尔显示器,DELL-2026,保存成功
student,student,机械键盘,KEY-99,保存成功
```

注意：`expected_alert` 必须与系统真实弹窗文案完全一致（如“保存成功”）。

---

## 5. 路径规范（关键）

禁止硬编码 Windows 路径（如 `C:\...`）。  
统一使用脚本锚点路径，避免“从不同目录启动导致路径失效”。

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "assets_data.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "..", "screenshots")
```

---

## 6. 自动化流程（23 步映射）

### 6.1 初始化与登录（1-11）

- 导入 webdriver / By / time 等
- 创建 Firefox 驱动
- `maximize_window()` + `set_window_size(1920, 1080)`
- 打开登录页：`http://10.65.8.254/pams/front/login.do`
- 设置隐式等待：`implicitly_wait(10)`
- 登录定位：
  - `By.ID`：`loginName`
  - `By.NAME`：`password`
  - `By.TAG_NAME`：`button` 点击登录

### 6.2 页面交互（12-20）

- 导航：`back()` -> `forward()` -> `refresh()`
- 资产类别入口：
  - `Partial Link Text` 或 `Link Text`
- 新增流程：
  - `By.CLASS_NAME` 点击“新增”
  - `By.NAME` 输入类别名称
  - `By.CSS_SELECTOR` 输入类别编码
  - `By.XPATH` 点击“保存”

### 6.3 弹窗与退出（21-23）

- `switch_to.alert.accept()`
- 返回欢迎页（如流程要求）
- 显式等待收尾（必要时）
- `quit()` 释放驱动

---

## 7. 框架与用例规范（unittest + ddt）

### 7.1 基础结构

- 测试类继承 `unittest.TestCase`
- `setUp()`：驱动初始化、窗口、等待
- `tearDown()`：`driver.quit()`
- 类装饰器：`@ddt.ddt`
- 方法装饰器：`@ddt.data(*get_test_data())`

### 7.2 Headless 规范

- CI 或无桌面环境：默认启用
- 本地调试：可关闭

```python
options.add_argument("--headless")
```

---

## 8. 等待与断言策略（必须双重断言）

### 8.1 等待策略

- 全局：隐式等待（10s）
- 关键交互：显式等待（`WebDriverWait`）
  - 登录跳转
  - 保存按钮可点击
  - 弹窗出现
  - 列表刷新后结果出现

### 8.2 双重断言（Double-Check）

1. 一级断言（Alert）  
- 等待弹窗出现
- 校验 `alert.text == expected_alert`
- `alert.accept()`

2. 二级断言（Page Level）  
- 关闭弹窗后，校验列表出现新增编码（`category_code`）
- 推荐 XPath 模板：

```python
f"//table//td[contains(., '{unique_code}')]"
```

---

## 9. 幂等性与异常处理

### 9.1 幂等性（避免重复冲突）

新增编码使用时间戳后缀：

```python
unique_code = f"{data[3]}_{int(time.time())}"
```

### 9.2 异常处理（失败可追溯）

发生异常时至少执行：

- 自动截图（确保目录存在）
- 输出截图路径
- 输出当前 URL、异常信息
- 保留异常抛出（不吞错）

示例命名：

```python
test_add_asset_category_20260326_153012.png
```

---

## 10. 数据读取工具规范

`get_test_data()` 建议具备以下能力：

- 跳过标题行
- 跳过空行
- 校验每行列数为 5
- 文件不存在时抛出带绝对路径的错误

---

## 11. 执行入口与报告输出

### 11.1 单文件执行

```bash
python3 tests/test_assets.py
```

### 11.2 批量发现执行

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### 11.3 统一入口（推荐）

`test_runner.py`：

```python
import os
import unittest
import xmlrunner

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    suite = unittest.TestLoader().discover("./tests", pattern="test_*.py")
    with open("reports/results.xml", "wb") as output:
        xmlrunner.XMLTestRunner(output=output).run(suite)
```

运行：

```bash
python3 test_runner.py
```

输出：`reports/results.xml`（JUnit 兼容）

---

## 12. 元素定位优先级（稳定性）

1. `ID` / `Name`（首选）
2. `CSS Selector`
3. `XPath`（最后手段，仅复杂结构/动态 DOM 时）

---

## 13. 最小验收标准（Definition of Done）

满足以下 4 条即视为通过：

1. 在项目根目录可一键执行测试（`python3 test_runner.py`）。
2. 成功生成报告：`reports/results.xml`。
3. 失败自动截图到 `screenshots/`。
4. 每个核心新增流程同时通过：
   - alert 文案断言
   - 页面列表结果断言

---

## 14. Copilot 使用建议（可选）

- 生成 XPath：
  `@workspace 基于这段 HTML，用 By.XPATH 补全保存按钮定位`
- 处理权限报错：
  `/fix 解释 geckodriver 权限报错并给出 chmod 修复命令`
- 生成 CSV：
  `把这段资产数据转成 data/assets_data.csv（ddt 可直接读取）`
