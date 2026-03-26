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