# 网页爬取
import requests # 导入requests库：用于发送 HTTP 请求获取网页内容
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据
import pandas # 抓取的网页数据利用pandas库转换为csv文件存储
import time
import sqlite3
from readability import Document # readability 是一个网页正文提取工具，可以从 HTML 页面中提取出主要内容
# import jieba
from concurrent.futures import ThreadPoolExecutor
from keyword_extractor import extract_keywords  # 引入关键词提取模块
from collections import deque

# 连接 SQLite 数据库
conn = sqlite3.connect("articles.db")
cursor = conn.cursor() # 创建一个游标对象，执行SQL语句（查询、插入、更新等）
cursor.execute('''CREATE TABLE IF NOT EXISTS pages 
                  (id INTEGER PRIMARY KEY, title TEXT, url TEXT, content TEXT, keywords TEXT)''')# 创建一个名为pages的表
conn.commit() # 提交 SQL 语句的更改，让数据库保存创建的 pages 表

#字段解释
#字段名	数据类型	说明
#id	INTEGER PRIMARY KEY	主键，自动递增，唯一标识每个网页
#title	TEXT	网页标题
#url	TEXT	网页链接
#content	TEXT	网页正文内容（爬取的文本）
#keywords	TEXT	关键词（用于搜索优化）

# 设置目标网址
# 访问过的 URL，避免重复爬取
visited_urls = set()
# url = 'https://www.baidu.com/'

# 抓取网页函数
def fetch_page(url):
    headers = {
        'User-Agent': 'studyCrawler (+https://github.com/l1xiaobei/Python_SearchEngine)'
    }
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
            response = requests.get(url, headers=headers, timeout=10)  # 设置超时时间，避免卡住，单位为秒
            response.raise_for_status()  # 该方法用于检查 HTTP 响应状态码，如果 HTTP 状态码不是 200，则抛出异常requests.exceptions.HTTPError
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[提示信息].抓取网页时出现错误,第 {i+1} 次请求失败: {e}")
            time.sleep(2)  # 休息 2 秒后重试
    
# 使用 BeautifulSoup 解析 HTML 页面
def parse_page(base_url,to_crawl):
    if not base_url or base_url in visited_urls:
        return None
    visited_urls.add(base_url)# 记录已爬取 URL
    html = fetch_page(base_url) 
    if not html:
        return None
    soup = BeautifulSoup(html, 'lxml') # 使用lxml解析器解析爬取到的html网页内容
        # 提取标题
        # title = soup.find('title')
        # if soup.find('title'):
        #     title = soup.find('title').get_text()
        # else:
        #     print('[提示信息].抓取不到标题!') # 加一个验证确保标题存在
    title = soup.find('title').get_text() if soup.find('title') else (print("[提示信息].抓取不到标题!") or '')
        # 提取正文
        # body = soup.find('body')
        # if soup.find('body'):
        #     body = soup.find('body').get_text()
        # else:
        #     print('[提示信息].抓取不到正文!') # 加一个验证确保正文存在
    body = soup.find('body').get_text() if soup.find('body') else (print("[提示信息].抓取不到正文!") or '')
    # 提取正文 使用readability库
    #doc = Document(html) # 解析 HTML，自动识别正文 
    #body = doc.summary() if doc.summary() else (print("[提示信息].抓取不到正文!") or '')# 获取主要内容（以 HTML 格式输出）
        # 提取日期
        # date = soup.find('span', {'class': 'publish-date'}).get_text() # 提取网页日期
        # author = soup.find('span', {'class': 'author-name'}).get_text() # 提取作者信息
        ##临时
            # 输出标题和部分正文内容（为了避免打印过多文本，这里只输出前500个字符）
    # 提取关键词
    # keywords = ",".join(jieba.analyse.extract_tags(body, topK=5))
    # 使用 extract_keywords 自动提取关键词（支持中英文）
    keywords = extract_keywords(body, topK=5)
    
    #从页面中提取链接
    links = []
    for link in soup.find_all('a', href=True):
        url = link['href']
        # 处理相对路径（如 "/page1" → 转为完整 URL）
        full_url = requests.compat.urljoin(base_url, url)
        if full_url not in visited_urls and full_url not in to_crawl:
            links.append(full_url)

    print(f"[提示信息].成功抓取: {url}")
    print(f"[提示信息].标题: {title}\n关键词: {keywords}\n")

    return title, url, body, keywords,links

# 存储数据到 SQLite
def save_to_db(title, url, body, keywords):
    cursor.execute("INSERT INTO pages (title, url, content, keywords) VALUES (?, ?, ?, ?)",
                   (title, url, body, keywords))
    conn.commit()

# def save_page(url):
#     result = parse_page(url)
#     if result:
#         title, body = result 
#         # 将抓取的数据存储为 CSV 文件
#         # 创建字典data
#         data = {'title': [title], 'link': [url], 'body': [body]}
#         # 这里的中括号 [ ] 用于创建包含单个元素的列表
#         # 在 Pandas 中，DataFrame 是一个二维的、表格型的数据结构，需要行和列来组织数据。
#         # 当创建一个 DataFrame 时，如果提供的数据是单个值而不是列表或数组，
#         # Pandas 会将其视为标量值，并抛出一个错误，因为它不知道如何将这些标量值组织成行和列。
#         # 通过将每个值包装在列表中，可以明确地告诉 Pandas 每个值应该被视为一个单独的元素，
#         # 而不是整个 DataFrame 的列。
#         # 这样，Pandas 就可以正确地将这些数据转换为 DataFrame，每个列表中的元素对应 DataFrame 的一行。
#         df = pandas.DataFrame(data) # df即dataframe，是一个表格类型的数据结构
#         df.to_csv('articles.csv', index=True) # 将df保存为名为articles的csv文件
#     else:
#         print("[提示信息].无法解析页面!")

# 爬虫调度
# def start_crawler(start_urls, max_pages=10):
#     to_crawl = set(start_urls)
#     crawled = set()
    
#     with ThreadPoolExecutor(max_workers=5) as executor:  # 线程爬取
#         while to_crawl and len(crawled) < max_pages:
#             url = to_crawl.pop()
#             new_links = executor.submit(parse_page, url).result()
#             if new_links:
#                 save_to_db(*new_links)
#             crawled.add(url)

#     print(f"\n[提示信息].爬取完成，已爬取 {len(crawled)} 个网页")

def start_crawler(start_urls):
    to_crawl = deque(start_urls)  # 用队列存储待爬取 URL（广度优先）
    visited_urls = set()  # 存储已访问 URL
    
    while to_crawl:
        url = to_crawl.popleft()  # 先进先出，保证广度优先
        if url in visited_urls:
            continue  # 避免重复爬取
        
        print(f"\n[正在爬取] {url}")
        result = parse_page(url,to_crawl)  # 解析页面
        if result:
            title, url, body, keywords,links = result
            save_to_db(title, url, body, keywords)
            visited_urls.add(url)

            # 提取新链接并去重后加入待爬队列
            new_links = set(links) - visited_urls  # 只添加未访问的
            to_crawl.extend(new_links)  

    print(f"\n🎯 爬取完成，共爬取 {len(visited_urls)} 个网页")
# 启动爬虫
start_urls = ["https://www.baidu.com",
              "https://finance.sina.com.cn/",
              "https://www.huxiu.com/channel/115.html",
              "https://www.eastmoney.com/",
              "https://wallstreetcn.com/",
              "https://www.thepaper.cn/channel_25951"
              ]
#百度、新浪财经、虎嗅财经、东方财富、华尔街见闻，澎湃新闻
start_crawler(start_urls)

# 关闭数据库
conn.close()