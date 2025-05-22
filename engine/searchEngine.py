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
                "timestamp": source.get("timestamp", "").replace("T", " ")[:16], # 只保留日期部分 # 更新 保留到分钟ver0.1.2
                "score": hit["_score"]  # [DEBUG] 查看相关性得分
            })
        return results

    def getMacro(self, source, page=1, per_page=10):
        """获取指定来源的最新政策（带分页）"""
        # 构建分页查询
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"source": source}}  # 精确匹配来源
                    ]
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}],  # 按时间降序
            "from": (page-1)*per_page,
            "size": per_page,
            "_source": ["title", "content", "source", "timestamp", "url"]  # 限制返回字段
        }

        try:
            response = self.es.search(index=self.index_name, body=query)
            total = response['hits']['total']['value']  # 获取总记录数
            total_pages = (total + per_page - 1) // per_page  # 计算总页数

            results = []
            for hit in response["hits"]["hits"]:
                source_data = hit["_source"]
                results.append({
                    "title": source_data.get("title", "无标题"),
                    "content": source_data.get("content", "")[:200] + "...",  # 截取内容摘要
                    "source": source_data.get("source", "未知来源"),
                    "timestamp": source_data.get("timestamp", "").replace("T", " ")[:16],  # 格式化日期 # 更新 保留到分钟ver0.1.2
                    "url": source_data.get("url", "#")
                })

            return {
                "policies": results,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_items": total
                }
            }
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return {"policies": [], "pagination": {}}
    
    def getNews(self, size=10):
        """获取最新新闻（每个来源仅保留最新的一条）"""
        try:
            # 构建ES查询（按时间倒序获取足够数据用于去重）
            query = {
                "query": {"match_all": {}},
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": 50,  # 获取前50条用于去重筛选
                "_source": ["title", "url", "timestamp", "source"]
            }

            response = self.es.search(index=self.index_name, body=query)
            
            # 去重处理（保留每个来源最新的一条）
            seen_sources = set()
            news_list = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                current_source = source.get("source", "未知来源")
                
                if current_source not in seen_sources:
                    seen_sources.add(current_source)
                    news_list.append({
                        "title": source.get("title", "无标题"),
                        "url": source.get("url", "#"),
                        "timestamp": source.get("timestamp", "").replace("T", " ")[:16], # 截取日期部分 # 更新 保留到分钟ver0.1.2
                        "source": current_source
                    })
                
                if len(news_list) >= size:
                    break

            return news_list

        except Exception as e:
            print(f"新闻查询失败: {str(e)}")
            return []
