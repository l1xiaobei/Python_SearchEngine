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
                    },# 这个原始 _score 就是 Elasticsearch 的文本相关性得分。
                    # "boost_mode": "sum",
                    "boost_mode": "multiply", # 最终得分 = 文本匹配得分 × 时间得分
                    "score_mode": "sum", # 合并多个function 但这里只有一个，故score_mode: "sum" 就是函数得分 = 时间得分
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
                    "title": {

                    },
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
                "content": highlight.get("content", [source["content"][:200]])[0] + "...",
                "source": source.get("source", ""),
                "timestamp": source.get("timestamp", "")[:10], # 只保留日期部分
                "score": hit["_score"]  # [DEBUG] 查看相关性得分
            })
        return results
