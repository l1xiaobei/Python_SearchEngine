from elasticsearch import Elasticsearch

class SearchEngine:
    def __init__(self, index_name="financial_database"):
        """连接到 Elasticsearch 并指定索引"""
        self.es = Elasticsearch("http://localhost:9200")
        self.index_name = index_name

    def search(self, query):
        """在 Elasticsearch 进行搜索"""
        if not query:
            return []

        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]  # 在标题和正文中搜索
                }
            }
        }

        response = self.es.search(index=self.index_name, body=es_query)

        results = []
        for hit in response["hits"]["hits"]:
            results.append({
                "title": hit["_source"]["title"],
                "url": hit["_source"]["url"],
                "content": hit["_source"]["content"][:200] + "..."  # 显示前200个字符
            })
        return results
