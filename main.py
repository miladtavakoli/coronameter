from crawl.crawl_daily_table import CrawlWorldMeter
from domain.country_domain import CountryDomain
from repository.countries import CountriesRepository
from repository.death_daily import DeathReportRepository
from repository.log_repo import CrawlerLogRepository
from repository.newcase_daily import CaseReportRepository
from repository.statics_daily_log import StaticsRepository
from use_case import country_usecase, log, main_crawler
from use_case.draw_graph import CreateCountryStaticsPlotUseCase, CreateComparisonPlotUseCase
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


def get_country_data_days_ago(country, how_many_days_ago):
    use_case = CreateCountryStaticsPlotUseCase(new_case_repo=CaseReportRepository(), death_repo=DeathReportRepository())
    return use_case.execute(country, how_many_days_ago)


def get_comparison(first_country: str, second_country: str, how_many_days_ago: int):
    """
        Comparison of statistics between the two countries in terms of population
        :param first_country: name of country
        :param second_country: name of another country
        :param how_many_days_ago: integer
        :return: plot.show()
    """
    use_case = CreateComparisonPlotUseCase(country_repo=CountriesRepository(),
                                           new_case_repo=CaseReportRepository(),
                                           death_repo=DeathReportRepository())
    return use_case.execute(first_country, second_country, how_many_days_ago)


if __name__ == '__main__':
    # r = get_comparison("iran", "usa", how_many_days_ago=50)
    r = update_report_now_table()
    print(r)
