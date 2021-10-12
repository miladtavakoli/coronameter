from celery import group
from celery_app.tasks import crawl_data


class CeleryCrawlWorldMeterUseCase:
    def __init__(self, main_table_crawler):
        self.main_table_crawler = main_table_crawler()

    def execute(self):
        country_links = self.main_table_crawler.get_country_link()
        lazy_group = group([crawl_data.s(country, link) for country, link in country_links.items()])
        lazy_group()
        return "Done"
