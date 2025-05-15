# from elasticsearch import Elasticsearch

# class SearchEngine:
#     def __init__(self, index_name="financial_articles"):
#         """连接到 Elasticsearch 并指定索引"""
#         self.es = Elasticsearch("http://localhost:9200")
#         self.index_name = index_name

#     def search(self, query):
#         """在 Elasticsearch 进行搜索"""
#         if not query:
#             return []

#         es_query = {
#             "query": {
#                 "multi_match": {
#                     "query": query,
#                     "fields": ["title", "content"]  # 在标题和正文中搜索
#                 }
#             }
#         }

#         response = self.es.search(index=self.index_name, body=es_query)

#         results = []
#         for hit in response["hits"]["hits"]:
#             results.append({
#                 "title": hit["_source"]["title"],
#                 "url": hit["_source"]["url"],
#                 "content": hit["_source"]["content"][:200] + "..."  # 显示前200个字符
#             })
#         return results
from elasticsearch import Elasticsearch

class SearchEngine:
    def __init__(self, index_name="financial_articles"):
        """连接到 Elasticsearch 并指定索引"""
        self.es = Elasticsearch("http://localhost:9200")
        self.index_name = index_name

    def search(self, query):
        """在 Elasticsearch 中进行搜索（含相关性排序和高亮）"""
        if not query:
            return []

        es_query = {
            "query": {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "content"]  # 标题加权
                        }
                    },
                    "boost_mode": "sum",
                    "score_mode": "sum",
                    "functions": [
                        {
                            "gauss": {
                                "timestamp": {  # 按发布时间衰减分数（越新越高）
                                    "origin": "now",
                                    "scale": "10d",
                                    "decay": 0.5
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 200,
                        "number_of_fragments": 1
                    }
                }
            }
        }

        response = self.es.search(index=self.index_name, body=es_query)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            highlight = hit.get("highlight", {})

            results.append({
                "title": highlight.get("title", [source["title"]])[0],
                "url": source["url"],
                "content": highlight.get("content", [source["content"][:200]])[0] + "..."
            })
        return results
