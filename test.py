import requests # 导入requests库：用于发送 HTTP 请求获取网页内容
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据
import pandas # 抓取的网页数据利用pandas库转换为csv文件存储

# 设置目标网址
url = 'https://www.baidu.com/'
#headers = {
#     'User-Agent': 'studyCrawler (+https://github.com/l1xiaobei/Python_SearchEngine)'
#}

# 抓取网页函数
def fetch_page(url):
    #response = requests.get(url, headers=headers)
    response = requests.get(url)
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
        soup = BeautifulSoup(html, 'lxml') # 使用lxml解析器解析爬取到的html网页内容
        # 提取标题
        # title = soup.find('title')
        # if soup.find('title'):
        #     title = soup.find('title').get_text()
        # else:
        #     print('[提示信息].抓取不到标题!') # 加一个验证确保标题存在
        title = soup.find('title').get_text() if soup.find('title') else print('[提示信息].抓取不到标题!')
        # 提取正文
        # body = soup.find('body')
        # if soup.find('body'):
        #     body = soup.find('body').get_text()
        # else:
        #     print('[提示信息].抓取不到正文!') # 加一个验证确保正文存在
        body = soup.find('body').get_text() if soup.find('body') else print('[提示信息].抓取不到正文!')
        # 提取日期
        # date = soup.find('span', {'class': 'publish-date'}).get_text() # 提取网页日期
        # author = soup.find('span', {'class': 'author-name'}).get_text() # 提取作者信息
        ##临时
            # 输出标题和部分正文内容（为了避免打印过多文本，这里只输出前500个字符）
        print("标题:", title)
        #print("日期:", date)
        #print("正文:", author)
        print("\n正文（部分）：", body[:500])  # 打印正文的前500个字符   
        ##临时
        return title, body
    else:
        return None 

def save_page(url):
    result = parse_page(url)
    if result:
        title, body = result 
        # 将抓取的数据存储为 CSV 文件
        data = {'title': [title], 'link': [url], 'body': [body]}
        # 这里的中括号 [ ] 用于创建包含单个元素的列表
        # 在 Pandas 中，DataFrame 是一个二维的、表格型的数据结构，需要行和列来组织数据。
        # 当创建一个 DataFrame 时，如果提供的数据是单个值而不是列表或数组，
        # Pandas 会将其视为标量值，并抛出一个错误，因为它不知道如何将这些标量值组织成行和列。
        # 通过将每个值包装在列表中，可以明确地告诉 Pandas 每个值应该被视为一个单独的元素，
        # 而不是整个 DataFrame 的列。
        # 这样，Pandas 就可以正确地将这些数据转换为 DataFrame，每个列表中的元素对应 DataFrame 的一行。
        df = pandas.DataFrame(data) # df即dataframe，是一个表格类型的数据结构
        df.to_csv('articles.csv', index=True) # 将df保存为名为articles的csv文件
    else:
        print("[提示信息].无法解析页面!")


save_page(url)