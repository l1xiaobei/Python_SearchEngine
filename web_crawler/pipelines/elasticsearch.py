from elasticsearch import Elasticsearch
from datetime import datetime

class ElasticsearchPipeline:
    def __init__(self, index_name="financial_articles", es_host="http://localhost:9200"):
        self.index_name = index_name
        self.es = Elasticsearch(es_host)

        # 如果索引不存在，则创建，且添加ik_smart分词配置
        if not self.es.indices.exists(index=self.index_name):
            body = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "ik_smart_analyzer": {
                                "type": "ik_smart"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "ik_smart",
                            "search_analyzer": "ik_smart"
                        },
                        "url": {
                            "type": "keyword"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "ik_smart",
                            "search_analyzer": "ik_smart"
                        },
                        "timestamp": {
                            "type": "date"
                        },
                        "source": {
                            "type": "keyword"
                        }
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=body)

    def save(self, article):
        required_fields = ["title", "url", "content", "timestamp", "source"]
        missing_fields = [k for k in required_fields if k not in article]

        if missing_fields:
            print(f"[警告] 缺失字段：{missing_fields}，跳过：{article.get('title')}")
            return

        try:
            self.es.index(index=self.index_name, id=article["url"], document=article)
            print(f"[ES] 成功保存文章：{article['title']}")
        except Exception as e:
            print(f"[ES错误] 无法保存文章：{article['title']}\n原因：{e}")
