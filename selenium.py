import functools

from selenium.webdriver.chrome.webdriver import WebDriver

from libs.log import i


def cus_webdriver(chromedriverPath, headless=True):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    d = DesiredCapabilities.CHROME
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    if headless:
        chrome_options.add_argument('--headless')  # 使用无头浏览器 #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36')
    # 浏览器启动默认最大化
    chrome_options.add_argument("--start-maximized")
    # 该处替换自己的chrome驱动地址
    browser = webdriver.Chrome(chromedriverPath, chrome_options=chrome_options, desired_capabilities=d)
    browser.set_page_load_timeout(20)
    return browser


def selenium(chromedriverPath='D://chromedriver.exe', headless=False, debug=False):
    """ 方法执行时间 """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            browser: WebDriver = cus_webdriver(chromedriverPath, headless)
            try:
                kw.update({'browser': browser})
                r = func(*args, **kw)
                if not debug:
                    browser.implicitly_wait(3)
                    browser.quit()
                return r
            except Exception as e:
                i('selenium崩溃:%s' % e)
                browser.quit()

        return wrapper

    return decorator
