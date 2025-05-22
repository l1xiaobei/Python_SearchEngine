from adapters.sina_adapter import SinaFinanceAdapter
from adapters.gov_adpater import GovAdapter
from pipelines.elasticsearch import ElasticsearchPipeline

adapters = [
    GovAdapter(),
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
