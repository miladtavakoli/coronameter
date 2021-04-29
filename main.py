from domain.country_domain import CountryDomain
from repository.countries import CountriesRepository
from repository.log_repo import CrawlerLogRepository
from use_case import country_usecase, log, main_crawler


def list_log():
    use_case = log.LogList(CrawlerLogRepository())
    res = use_case.execute()
    return res


def update_daily_report():
    use_case = main_crawler.UpdateDailyUseCase()
    return use_case.execute()


def crawl_history_statics():
    use_case = main_crawler.CrawlHistoryGraph()
    return use_case.execute()


def country_list():
    use_case = country_usecase.CountryList(CountriesRepository(), CountryDomain())
    return list(use_case.execute())


if __name__ == '__main__':
    r = country_list()
    print(r)
    print("I LOVE MYSelf")
