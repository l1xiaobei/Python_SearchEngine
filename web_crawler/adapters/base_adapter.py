#BaseAdapter用于统一所有适配器的基本功能。它通常用于封装共享的功能，避免在每个适配器中重复相同的代码。
#BaseAdapter 可以定义一些所有适配器共享的基本功能或方法，例如：
#抓取网页的基本方法（fetch_page）。
#解析网页的一些通用操作。
#可以包含日志记录、异常处理等通用功能。
#通过创建基础适配器类 BaseAdapter，其他具体适配器类（如 SinaFinanceAdapter 和 CaixinAdapter）都继承自它。

import requests
from datetime import datetime,timezone
from dateutil import parser
from abc import ABC, abstractmethod  # 引入抽象基类模块 Abstract Base Classes
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据

class BaseAdapter(ABC):
    """
    基础适配器类，定义了所有适配器共有的基础方法。
    """
    name = ""  # 适配器名称

    @abstractmethod
    def crawl(self):
        """
        抽象方法，所有子类都需要实现该方法
        """
        pass

    def fetch_page(self, url):
        """
        抓取网页内容的方法，子类可以重用这个方法
        """
        print(f"[DEBUG] fetch_page() 被调用，准备请求: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        # response = requests.get(url, headers=headers)
        # response = requests.get(url)
        # if response.status_code == 200: # 检查响应是否成功
        #     response.encoding = 'utf-8'  # 处理中文乱码
        #     return response.text # 返回一个字符串，包含了从该 url 获取到的 HTML 页面。
        # else:
        #     print("[提示信息].抓取网页时出现错误，错误码为:" + str(response.status_code) + "!")
        #     return None
        # 使用try语句进行异常处理
        for i in range(3):  # 最多重试 3 次
            try:
                # response = requests.get(url)        
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)  # 设置超时时间，避免卡住，单位为秒
                response.raise_for_status()  # 该方法用于检查 HTTP 响应状态码，如果 HTTP 状态码不是 200，则抛出异常requests.exceptions.HTTPError
                response.encoding = 'utf-8'
                print(f"[DEBUG] 成功抓取页面: {url}，内容长度: {len(response.text)}")
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"[提示信息].抓取网页时出现错误,第 {i+1} 次请求失败: {e}\n")
                time.sleep(2)  # 休息 2 秒后重试
        return None

    def extract_timestamp(self, soup):
        """
        提取时间戳的通用方法，适用于大多数适配器
        """
        time_meta = soup.find('meta', {'name': 'pubdate'})
        if time_meta and time_meta.get('content'):
            timestamp = parser.parse(time_meta['content'])
        else:
            timestamp = datetime.now()  # 默认当前时间

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)  # 赋予时区信息
        return timestamp
