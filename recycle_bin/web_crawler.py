from elasticsearch import Elasticsearch
import requests # 导入requests库：用于发送 HTTP 请求获取网页内容
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据
import pandas # 抓取的网页数据利用pandas库转换为csv文件存储
import time
#import sqlite3
#from readability import Document # readability 是一个网页正文提取工具，可以从 HTML 页面中提取出主要内容
# import jieba
from concurrent.futures import ThreadPoolExecutor
#from keyword_extractor import extract_keywords  # 引入关键词提取模块
from collections import deque
from urllib.parse import urljoin, urlparse
from datetime import datetime
from dateutil import parser
from dateutil.tz import UTC
# # 连接 SQLite 数据库
# conn = sqlite3.connect("articles.db")
# cursor = conn.cursor() # 创建一个游标对象，执行SQL语句（查询、插入、更新等）
# cursor.execute('''CREATE TABLE IF NOT EXISTS pages 
#                   (id INTEGER PRIMARY KEY, title TEXT, url TEXT, content TEXT, keywords TEXT)''')# 创建一个名为pages的表
# conn.commit() # 提交 SQL 语句的更改，让数据库保存创建的 pages 表

#字段解释
#字段名	数据类型	说明
#id	INTEGER PRIMARY KEY	主键，自动递增，唯一标识每个网页
#title	TEXT	网页标题
#url	TEXT	网页链接
#content	TEXT	网页正文内容（爬取的文本）
#keywords	TEXT	关键词（用于搜索优化）

# 连接到 Elasticsearch
es = Elasticsearch("http://localhost:9200")
# 检查集群健康状态
health = es.cluster.health()
print(f"[提示信息].elasticsearch状态：{health}\n")  # 正常会返回状态信息，如 {"status": "green", ...}
# 定义索引名称（类似数据库的表）
index_name = "financial_database"
# 如果索引不存在，则创建
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

# 访问过的 URL，避免重复爬取
visited_urls = set()

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
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)  # 设置超时时间，避免卡住，单位为秒
            response.raise_for_status()  # 该方法用于检查 HTTP 响应状态码，如果 HTTP 状态码不是 200，则抛出异常requests.exceptions.HTTPError
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[提示信息].抓取网页时出现错误,第 {i+1} 次请求失败: {e}\n")
            time.sleep(2)  # 休息 2 秒后重试
    return None
    
# 解析 HTML 页面
def parse_page(base_url,to_crawl):

    if not base_url or base_url in visited_urls:
        print(f"[提示信息].爬取网页网址为空值或该网址位于visited_urls中！\n")
        return None
    visited_urls.add(base_url)# 记录已爬取 URL

    html = fetch_page(base_url) 
    if not html:
        print(f"[提示信息].网页抓取异常，无法解析！\n")
        return None
    
    soup = BeautifulSoup(html, 'lxml') # 使用lxml解析器解析爬取到的html网页内容
        # 提取标题
        # title = soup.find('title')
        # if soup.find('title'):
        #     title = soup.find('title').get_text()
        # else:
        #     print('[提示信息].抓取不到标题!') # 加一个验证确保标题存在
    title = soup.find('title').get_text() if soup.find('title') else (print("[提示信息].抓取不到标题!\n") or '')
        # 提取正文
        # body = soup.find('body')
        # if soup.find('body'):
        #     body = soup.find('body').get_text()
        # else:
        #     print('[提示信息].抓取不到正文!') # 加一个验证确保正文存在
    body = soup.find('body').get_text() if soup.find('body') else (print("[提示信息].抓取不到正文!\n") or '')
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
    #keywords = extract_keywords(body, topK=5)
    
 # 从页面中提取链接
    links = []
    for link in soup.find_all('a', href=True):
        url = link['href']
        full_url = urljoin(base_url, url)  # 转换为完整 URL
        # 解析 URL
        parsed_url = urlparse(full_url)
        # 只保留 http 或 https 链接，排除空链接、锚点、JavaScript等
        if parsed_url.scheme not in ["http", "https"]:
            continue
        # 避免重复
        if full_url not in visited_urls and full_url not in to_crawl:
            links.append(full_url)
    
# ===== 新增时间提取逻辑 =====
    timestamp = None
    
    # 候选的元数据选择器列表（按优先级排序）
    meta_selectors = [
        {'property': 'article:published_time'},        # 主流新闻网站
        {'property': 'og:published_time'},            # Open Graph协议
        {'itemprop': 'datePublished'},                # Schema.org
        {'name': 'pubdate'},                          # 通用发布日
        {'name': 'publishdate'},                      # 常见CMS
        {'name': 'timestamp'},                        # 论坛类站点
        {'name': 'date'},                             # 通用日期
        {'http-equiv': 'date'},                       # HTTP等效头
        {'name': 'DC.date.issued'},                   # 都柏林核心元数据
        {'name': 'sailthru.date'},                    # 部分媒体专用
        {'name': 'parsely-pub-date'},                 # Parsely分析平台
    ]

    # 方案1：优先检查meta标签
    for selector in meta_selectors:
        meta_tag = soup.find('meta', selector)
        if meta_tag and meta_tag.get('content'):
            time_str = meta_tag['content'].strip()
            try:
                # 使用更智能的时间解析库
                timestamp = parser.parse(time_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)  # 默认补充UTC时区
                break
            except (ValueError, OverflowError, TypeError) as e:
                continue

    # 方案2：检查常见时间标签
    if not timestamp:
        time_tags = soup.find_all(['time', 'span', 'div', 'p'], class_=[
            'publish-time',
            'time',
            'date',
            'art-time',
            'pubtime',
            'timestamp',
            'post-date',
            'article-date',
            'dateline',
            'meta-time'
        ])
        
        for tag in time_tags:
            # 获取最内层文本并清洗
            raw_time = ' '.join(tag.stripped_strings)
            if not raw_time:
                continue
                
            # 清洗常见干扰字符
            clean_time = raw_time.split('|')[0].split('•')[0].strip('发布时间：')
            try:
                timestamp = parser.parse(clean_time, fuzzy=True)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)
                break
            except (ValueError, OverflowError) as e:
                continue

    # 方案3：检查标题中的时间信息
    if not timestamp:
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            try:
                # 从标题开头/结尾提取时间
                timestamp = parser.parse(title_text.split('-')[0], fuzzy=True) or \
                            parser.parse(title_text.split('|')[-1], fuzzy=True)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)
            except:
                pass

    # 最终回退逻辑
    if not timestamp:
        timestamp = datetime.now(UTC)  # 使用带时区的当前时间
        
    # 统一转换为UTC时间
    if timestamp.tzinfo:
        timestamp = timestamp.astimezone(UTC)
    else:
        timestamp = timestamp.replace(tzinfo=UTC)
    # ===== 时间提取结束 =====

    # 存入 Elasticsearch
    doc = {
        "title": title,
        "url": url,
        "content": body,
        "timestamp": timestamp.isoformat()  # 新增时间字段
    }
    es.index(index=index_name, document=doc)

    print(f"[提示信息].成功抓取: {url}\n时间戳: {timestamp}")
    #print(f"[提示信息].标题: {title}\n关键词: {keywords}\n")
    print(f"[提示信息].标题: {title}\n")


    return links

# # 存储数据到 SQLite（已弃用，直接在parse_page函数中将网页存储至elasticsearch）
# def save_to_db(title, url, body, keywords):
#     cursor.execute("INSERT INTO pages (title, url, content, keywords) VALUES (?, ?, ?, ?)",
#                    (title, url, body, keywords))
#     conn.commit()

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

# 启动爬虫
def start_crawler(start_urls):
    to_crawl = deque(start_urls)  # 队列存储待爬取 URL（广度优先）

    while to_crawl:
        url = to_crawl.popleft()  # 先进先出，广度优先
        new_links = parse_page(url, to_crawl)
        if new_links:
            to_crawl.extend(new_links)  # 加入新发现的链接

    print(f"[提示信息].爬取完成，共爬取 {len(visited_urls)} 个网页\n")

# 爬取的网址
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