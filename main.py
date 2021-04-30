from crawl.crawl_daily_table import CrawlWorldMeter
from domain.country_domain import CountryDomain
from repository.countries import CountriesRepository
from repository.death_daily import DeathReportRepository
from repository.log_repo import CrawlerLogRepository
from repository.newcase_daily import CaseReportRepository
from repository.statics_daily_log import StaticsRepository
from use_case import country_usecase, log, main_crawler
from use_case.main_crawler import UpdateLatestStaticsUseCase


def list_log():
    use_case = log.LogList(CrawlerLogRepository())
    res = use_case.execute()
    return res


def update_report_now_table(yesterday: bool = False):
    use_case = UpdateLatestStaticsUseCase(crawler=CrawlWorldMeter(),
                                          log_repo=CrawlerLogRepository(),
                                          statics_repo=StaticsRepository(),
                                          countries_repo=CountriesRepository(),
                                          new_case_repo=CaseReportRepository(),
                                          death_repo=DeathReportRepository(),
                                          )
    return use_case.execute(yesterday=yesterday)


def update_report_yesterday_table():
    # use_case = main_crawler.UpdateYesterdayStaticsUseCase()
    # return use_case.execute()
    pass


def save_history_statics():
    use_case = main_crawler.CrawlHistoryGraph()
    return use_case.execute()


def country_list():
    use_case = country_usecase.CountryList(CountriesRepository(), CountryDomain())
    return list(use_case.execute())


if __name__ == '__main__':
    r = update_report_now_table(yesterday=False)
    print(r)
