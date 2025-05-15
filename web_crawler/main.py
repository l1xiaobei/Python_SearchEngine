from adapters.sina_adapter import SinaFinanceAdapter
from pipelines.elasticsearch import ElasticsearchPipeline

adapters = [
    SinaFinanceAdapter(),
    # 可添加更多 adapter
]

pipeline = ElasticsearchPipeline()

def run():
    for adapter in adapters:
        print(f"[调度器] 开始爬取: {adapter.name}")
        for article in adapter.crawl():
            pipeline.save(article)

if __name__ == "__main__":
    run()
