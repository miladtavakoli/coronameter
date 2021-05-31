from crawl.crawl_graph import CrawlDailyStatics
from repository.death_daily import DeathReportRepository
from repository.newcase_daily import CaseReportRepository
from .celery import app
from .tools import _rebuild_item


@app.task
def crawl_data(country, link):
    case_repo = CaseReportRepository()
    death_repo = DeathReportRepository()
    crawl_daily_graph = CrawlDailyStatics(link)
    result = crawl_daily_graph.execute()
    print(country)
    # check cases statistics and save
    if result.death_daily is not None and len(result.death_daily) > 0:
        items = [_rebuild_item(item, country) for item in result.death_daily]
        death_repo.insert_many(items=items)

    # check cases statistics and save
    if result.case_daily is not None and len(result.case_daily) > 0:
        items = [_rebuild_item(item, country) for item in result.case_daily]
        case_repo.insert_many(items=items)

    return None
