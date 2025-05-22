from adapters.base_adapter import BaseAdapter
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re
import time

class GovAdapter(BaseAdapter):
    name = "中国政府网-政策文件"

    def crawl(self):
        base_url = "https://www.gov.cn/zhengce/zuixin/home.htm"
        page_number = 0
        self.visited_urls = set()

        while True:
            # 政策页面分页规律：home.htm, home_1.htm, home_2.htm, ...
            if page_number == 0:
                url = base_url
            else:
                url = f"https://www.gov.cn/zhengce/zuixin/home_{page_number}.htm"

            html = self.fetch_page(url)
            if not html:
                print(f"[DEBUG] 页面获取失败：{url}")
                break

            soup = BeautifulSoup(html, 'html.parser')
            link_tags = soup.select('div.list.list_1 li a')
            if not link_tags:
                print(f"[DEBUG] 没有更多链接，结束分页抓取。page: {page_number}")
                break

            for tag in link_tags:
                article_url = urljoin(url, tag['href'])
                if article_url in self.visited_urls or not self.should_visit(article_url):
                    continue
                self.visited_urls.add(article_url)

                article_html = self.fetch_page(article_url)
                if not article_html:
                    continue

                for article in self.parse_page(article_url, article_html):
                    yield article

            page_number += 1
            time.sleep(1)  # 避免请求过快被封禁

    def should_visit(self, url):
        return url.startswith("https://www.gov.cn/") and url.endswith(".htm")

    def parse_page(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('h1')
        content_div = soup.find('div', class_='pages_content') or soup.find('div', class_='article-content')
        source_tag = soup.find('span', class_='source')
        date_tag = soup.find('span', class_='pubtime') or soup.find(string=re.compile(r'\d{4}-\d{2}-\d{2}'))

        if title_tag and content_div:
            title = title_tag.get_text(strip=True)
            content = content_div.get_text(strip=True)
            source = source_tag.get_text(strip=True) if source_tag else "中国政府网"
            timestamp = self.extract_timestamp(date_tag)

            yield {
                "title": title,
                "url": url,
                "source": "政策库",
                "content": content,
                "timestamp": timestamp.isoformat(timespec='seconds') if timestamp else None
            }

    def extract_timestamp(self, date_tag):
        if not date_tag:
            return None
        date_text = date_tag.get_text(strip=True) if hasattr(date_tag, 'get_text') else date_tag.strip()
        
        match = re.search(r'\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}(?::\d{2})?)?', date_text)
        if match:
            try:
                date_str = match.group()
                if len(date_str) == 10:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                elif len(date_str) == 16:
                    return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                elif len(date_str) == 19:
                    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None
        return None
