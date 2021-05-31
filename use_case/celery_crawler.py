from celery import group
from celery_app.tasks import crawl_data


class CeleryCrawlWorldMeterUseCase:
    def __init__(self, crawler):
        self.crawler = crawler()

    def execute(self):
        country_links = self.crawler.get_country_link()
        lazy_group = group([crawl_data.s(country, link) for country, link in country_links.items()])
        lazy_group()
        return "Done"
