import requests # 导入requests库：用于发送 HTTP 请求获取网页内容
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据

# 设置目标网址
url = 'https://www.huxiu.com/moment/'
headers = {
     'User-Agent': 'studyCrawler (+https://github.com/l1xiaobei/Python_SearchEngine)'
}

# 抓取网页函数
def fetch_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200: # 检查响应是否成功
        response.encoding = 'utf-8'  # 处理中文乱码
        return response.text # 返回一个字符串，包含了从该 url 获取到的 HTML 页面。
    else:
        print("[提示信息].抓取网页时出现错误，错误码为:" + str(response.status_code) + "!")
        return None
        
    
# 使用 BeautifulSoup 解析 HTML 页面
def parse_page(url):
    html = fetch_page(url) 
    if html:
        soup = BeautifulSoup(html, 'html.parser') # 使用lxml解析器解析爬取到的html网页内容
        title = soup.title.string if soup.title else print('No Title') # 加一个验证确保标题存在
        body = soup.get_text()
        ##临时
            # 输出标题和部分正文内容（为了避免打印过多文本，这里只输出前500个字符）
        print("标题:", title)
        print("\n正文（部分）：", body[:500])  # 打印正文的前500个字符
        ##临时
        return title, body
    else:
        return None 


parse_page(url)