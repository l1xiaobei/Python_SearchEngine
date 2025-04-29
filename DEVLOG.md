# 开发日志

---

## 0.0.1 (2025-1-18)

### 改动

- 初始化git仓库，添加许可证，开发日志，README。

---

## 0.0.2 (2025-1-20)

### 改动

- 创建运行软件需要的虚拟环境，并添加/environment.yml文件。
- 创建/test.py文件测试网页爬虫是否可用。
- 创建/main.py文件尝试搭建一个flask框架应用。
- 创建/templates文件夹，用于存放flask应用的html界面文件。
- 创建/templates/index.html文件作为flask应用的主页html文件。

---

## 0.0.3 (2025-1-21)

### 改动

- /environment.yml文件中添加pandas库用于将网页保存为csv文件。
- 修改/test.py文件中爬取网页相关代码，添加了更为合理的验证爬取成功机制。
- 修改/main.py文件，添加了搜索处理的相关代码。
- 修改/test.py文件，添加了函数save_page()用于将网页链接、标题与正文保存为csv文件。

---

## 0.0.4 (2025-1-24)

### 改动

- 创建/engine文件夹，用于存放搜索引擎搜索相关代码。
- 创建/engine/search.py文件，创建searchEngine类用于搜索处理。
- 创建/templates/result.html用于存放搜索结果html文件。
- 创建.gitignore文件用于避免提交不必要的文件。
- 修改/main.py文件，通过调用/engine/search.py实现搜索处理的相关功能。

---

## 0.0.5 (2025-3-27)

### 改动

- 创建/keyword_extractor.py用于提取中英文网页关键词。
- 创建/articles.db用于作为新的网页数据存储数据库。
- 修改/test.py为/web_crawler.py。
- 修改/web_crawler.py文件:
  - 添加import time、import sqlite3、import readability、from keyword_extractor import extract_keywords；from concurrent.futures import ThreadPoolExecutor
  - 添加爬虫链接至数据库/articles.db相关代码；
  - 添加save_to_db()函数用于存储网页数据至数据库；
  - 添加start_crawler()函数用于启动爬虫；
  - 将user-agent调整至函数fetch_page中；
  - 使用try语句重构异常处理代码；
  - 修改函数parse_page()中提取正文、标题相关代码,添加返回''空字符串功能,添加防止重复爬取同一网页功能。

---

## 0.0.6 (2025-3-27)

### 改动

- 修改/web_crawler.py文件以进行爬取网页测试。
- 修改enviroment.yml文件以添加必要的库。

### 问题

/web_crawler.py爬取到的网页数据没有被很好的解析，正文和关键词与实际存在偏差。(已基本解决)

---

## 0.0.7 (2025-3-29)

### 改动

- 修改/web_crawler.py文件:
  - 使用beautifulsoup提取网页正文。
  - 添加from collections import deque。
  - 修改函数start_crawler，现在可以爬取多个网页。
- 修改/keyword_extractor.py文件，添加jieba加载中文停用词功能。

### 问题

- 提取网页链接接续爬取功能尚不完善，无法正常运行。

### 备注

- 开发方向调整为面向普通投资者的金融领域垂直搜索引擎。

---

## 0.0.8 (2025-3-30)

### 改动

- 修改/web_crawler.py文件:
  - 添加from elasticsearch import Elasticsearch、from urllib.parse import urljoin, urlparse。
  - 移除save_to_db函数，爬取到的网页不再存在sqlite数据库中，而在parse_page函数中将网页存至elasticsearch。
- 删除关键词提取功能，停用/keyword_extractor.py文件。
- 修改main.py、searchEngine.py以配合elasticsearch使用。

### 问题

- 一些网站存在反爬机制，爬取的网页链接不准确。需要研究爬取的各个网站的robots.txt。

## 0.0.9 (2025-4-28)

### 改动

- 修改/templates/index.html和/templates/result.html文件，重构搜索引擎的前端界面，使其看起来更美观和易于使用。


### 问题

- 对于/templates/index.html文件，当点击搜索框，搜索框周围会出现一个黑色的轮廓线，但这个轮廓线没有完全包裹搜索框的圆角，导致角落看起来不完整。

## 0.0.10 (2025-4-29)

### 改动

- 修改/web_crawler.py文件:
  - 添加from datetime import datetime，from dateutil import parser，from dateutil.tz import UTC，修改parse_page()函数，添加提取网页时间戳信息功能。