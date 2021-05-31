#!.venv/bin/python
import os

import click
from crawl.crawl_daily_table import CrawlWorldMeter
from domain.country_domain import CountryDomain
from repository.countries import CountriesRepository
from repository.death_daily import DeathReportRepository
from repository.log_repo import CrawlerLogRepository
from repository.newcase_daily import CaseReportRepository
from repository.statics_daily_log import StaticsRepository
from use_case import country_usecase, log, main_crawler,celery_crawler
from use_case.draw_graph import CreateCountryStaticsPlotUseCase, CreateComparisonPlotUseCase
from use_case.main_crawler import UpdateLatestStaticsUseCase
from celery_app.celery import app as celery_app_instance

@click.group()
def main():
    """
   ** Corona meter **
   \n
   A tool for tracking corona statistics and compare countries.
   Data was collected from : https://www.worldometers.info/coronavirus/
    """
    pass


@main.command()
def list_log():
    """
    list of last updates.
    :return:
    """
    use_case = log.LogList(CrawlerLogRepository())
    res = use_case.execute()
    for r in res:
        click.echo(r)


@main.command()
def update_latest():
    """
    update statics by now table in worldometer.com
    :return:
    """
    use_case = UpdateLatestStaticsUseCase(crawler=CrawlWorldMeter(),
                                          log_repo=CrawlerLogRepository(),
                                          statics_repo=StaticsRepository(),
                                          countries_repo=CountriesRepository(),
                                          new_case_repo=CaseReportRepository(),
                                          death_repo=DeathReportRepository(),
                                          )
    res = use_case.execute(yesterday=False)
    click.echo(res)


@main.command()
def update_yesterday():
    """
    update statics by yesterday table in worldometer.com
    :return:
    """
    use_case = UpdateLatestStaticsUseCase(crawler=CrawlWorldMeter(),
                                          log_repo=CrawlerLogRepository(),
                                          statics_repo=StaticsRepository(),
                                          countries_repo=CountriesRepository(),
                                          new_case_repo=CaseReportRepository(),
                                          death_repo=DeathReportRepository(),
                                          )
    res = use_case.execute(yesterday=True)
    click.echo(res)


@main.command()
def save_history():
    """
    crawl countries graph. save
    :return:
    """
    use_case = main_crawler.CrawlHistoryGraph()
    return use_case.execute()


@main.command()
def celery_save_history():
    """
    run celery.
    crawl countries graph. save
    :return:
    """

    worker = celery_app_instance.Worker()
    worker.start()
    use_case = celery_crawler.CeleryCrawlWorldMeterUseCase(CrawlWorldMeter)
    return use_case.execute()


@main.command()
def country_list():
    use_case = country_usecase.CountryList(CountriesRepository(), CountryDomain())
    result = list(use_case.execute())
    res = ""
    for counter, r in enumerate(result):
        res += f"{counter + 1}, {list(r.values())[0]}\n"
    click.echo(res)
    return None


@main.command()
@click.argument('country', nargs=1, )
@click.argument('how_many_days_ago', nargs=1, )
def get_country_graph(country, how_many_days_ago):
    if how_many_days_ago.isdigit():
        how_many_days_ago = int(how_many_days_ago)
    else:
        click.echo("enter number as days.")
    use_case = CreateCountryStaticsPlotUseCase(new_case_repo=CaseReportRepository(), death_repo=DeathReportRepository())
    return use_case.execute(country, how_many_days_ago)


@main.command()
@click.argument('first_country', nargs=1)
@click.argument('second_country', nargs=1)
@click.argument('how_many_days_ago', nargs=1)
def get_compare_graph(first_country: str, second_country: str, how_many_days_ago):
    """
        Comparison of statistics between the two countries in terms of population
        :param first_country: name of country
        :param second_country: name of another country
        :param how_many_days_ago: integer
        :return: plot.show()
    """
    if how_many_days_ago.isdigit():
        how_many_days_ago = int(how_many_days_ago)
    else:
        click.echo("enter number as days.")
    use_case = CreateComparisonPlotUseCase(country_repo=CountriesRepository(),
                                           new_case_repo=CaseReportRepository(),
                                           death_repo=DeathReportRepository())
    res = use_case.execute(first_country, second_country, how_many_days_ago)
    click.echo(res)


if __name__ == '__main__':
    main()
