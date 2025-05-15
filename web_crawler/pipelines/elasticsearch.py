from elasticsearch import Elasticsearch
#from elasticsearch.helpers import bulk 
#bulk 是 Elasticsearch 提供的“批量写入接口”，主要用于一次性写入多条文档数据
from datetime import datetime

class ElasticsearchPipeline:
    def __init__(self, index_name="financial_articles", es_host="http://localhost:9200"):
        self.index_name = index_name # 定义索引名称（类似数据库的表）
        self.es = Elasticsearch(es_host) # 连接到 Elasticsearch

        # 如果索引不存在，则创建
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body={
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "url": {"type": "keyword"},
                        "content": {"type": "text"},
                        "timestamp": {"type": "date"},
                        "source": {"type": "keyword"}
                    }
                }
            })

    def save(self, article):
        required_fields = ["title", "url", "content", "timestamp", "source"]
        missing_fields = [k for k in required_fields if k not in article]  # 收集缺失字段

        if missing_fields:
            print(f"[警告] 缺失字段：{missing_fields}，跳过：{article.get('title')}")
            # return

        try:
            self.es.index(index=self.index_name, id=article["url"], document=article)
            print(f"[ES] 成功保存文章：{article['title']}")
        except Exception as e:
            print(f"[ES错误] 无法保存文章：{article['title']}\n原因：{e}")

        return
