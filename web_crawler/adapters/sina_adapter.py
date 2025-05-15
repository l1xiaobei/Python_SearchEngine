from adapters.base_adapter import BaseAdapter
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re

class SinaFinanceAdapter(BaseAdapter):
    name = "新浪财经"

    def crawl(self):
        start_url = "https://finance.sina.com.cn/"
        to_crawl = [start_url]
        self.visited_urls = set()

        while to_crawl:
            url = to_crawl.pop(0)
            print(f"[DEBUG] 正在处理：{url}")
            #if url in self.visited_urls or not self.should_visit(url):
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            html = self.fetch_page(url)
            if not html:
                print(f"[DEBUG] 页面获取失败：{url}")
                continue

            # 解析文章并 yield
            for article in self.parse_page(url, html):
                print(f"[DEBUG] 抓到文章：{article['title']}")
                yield article

            # 解析新链接
            new_links = self.extract_links(url, html)
            print(f"[DEBUG] 提取新链接 {len(new_links)} 个")
            to_crawl.extend(new_links)

    def should_visit(self, url):
        # 只抓新浪财经站内新闻
        return url.startswith("https://finance.sina.com.cn/") and url.endswith(".shtml")

    def parse_page(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 提取标题
        title_tag = soup.find('div', class_='second-title')
        content_div = soup.find('div', class_='article') or soup.find('div', id='artibody')
        source_tag = soup.find('span', class_='source ent-source')

        if title_tag and content_div and source_tag:
            title = title_tag.get_text(strip=True)
            content = content_div.get_text(strip=True)
            timestamp = self.extract_timestamp(soup)
            source = source_tag.get_text(strip=True)

            yield {
                "title": title,
                "url": url,
                "source": source,
                "content": content,
                "timestamp": timestamp.isoformat(timespec='seconds') if timestamp else None # 将时间转换为iso 8601标准格式，输出截止到秒
                
            }

    def extract_links(self, base_url, html):
        soup = BeautifulSoup(html, 'html.parser')
        new_links = []

        for tag in soup.find_all('a', href=True):
            link = urljoin(base_url, tag['href'])
            if self.should_visit(link) and link not in self.visited_urls:
                new_links.append(link)

        return new_links

    def extract_timestamp(self, soup):
        # 新浪财经发布时间常见格式：<span class="date">2024年05月01日 11:33</span>
        time_tag = soup.find('span', class_=re.compile(r'date|time'))
        if time_tag:
            match = re.search(r'\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}', time_tag.get_text())
            if match:
                try:
                    return datetime.strptime(match.group(), "%Y年%m月%d日 %H:%M")
                except Exception:
                    pass
        return None
