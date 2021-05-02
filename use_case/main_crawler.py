from datetime import datetime, timedelta

from domain.country_domain import CountryDomain
from domain.log_domain import Log as LogDomain
from domain.newcases_domain import NewCaseDomain
from domain.newdeaths_domain import NewDeathDomain
from domain.statics_daily import StaticsDomain
from crawl.crawl_graph import CrawlDailyStatics
from crawl.crawl_daily_table import CrawlWorldMeter
from corona_meter_logger import logger
from repository.death_daily import DeathReportRepository
from repository.log_repo import CrawlerLogRepository
from repository.newcase_daily import CaseReportRepository
from repository.statics_daily_log import StaticsRepository
from tools import is_same_date


class CrawlHistoryGraph:
    def __init__(self):
        self.statics_repo = StaticsRepository()
        self.crawl_daily = CrawlWorldMeter()
        self.case_repo = CaseReportRepository()
        self.death_repo = DeathReportRepository()
        self.log_repo = CrawlerLogRepository()
        self.crawl_graph = CrawlDailyStatics

    def _crawl_countries(self):
        """
        Crawl list of country that exist in main table https://www.worldometers.info/coronavirus/
        :return
            dictionary {"iran" : "country/iran/"}
        """
        return self.crawl_daily.get_country_link()

    @staticmethod
    def _rebuild_item(item, country):
        item['created_at'] = datetime.now()
        item['updated_at'] = datetime.now()
        if isinstance(item['reported_at'], str):
            item['reported_at'] = datetime.strptime(item['reported_at'], "%b %d, %Y")
        if country is not None:
            item['country'] = country
        return item

    def crawl_daily_report(self, country_links: dict):
        """
        crawl history of statics from 'Daily Deaths' and 'Daily New Cases' graph.
        And save in database. in separated collections.

        :param
            country_links: dictionary of name of country and links that was crawl by _crawl_countries function.
        """
        counter = 0
        for country, link in country_links.items():
            crawl_daily_graph = self.crawl_graph(link)
            result = crawl_daily_graph.execute()
            len_death_daily = len_case_daily = 0

            if result.death_daily is not None and len(result.death_daily) > 0:
                len_death_daily = len(result.death_daily)
                items = [self._rebuild_item(item, country) for item in result.death_daily]
                self.death_repo.insert_many(items=items)

            if result.case_daily is not None and len(result.case_daily) > 0:
                len_case_daily = len(result.case_daily)
                items = [self._rebuild_item(item, country) for item in result.case_daily]
                self.case_repo.insert_many(items=items)

            counter += 1

            logger.debug(f"{counter},{country}__"
                         f"D:{len_death_daily},C:{len_case_daily}"
                         f" saved_at: {datetime.now()}")

        return "Done"

    def _crawl_log(self, started_at: datetime, command: str, count: int, status):
        l_ = LogDomain(command=command, count=count, started_at=started_at, status=status, ends_at=datetime.now())
        return self.log_repo.save(l_)

    def execute(self):
        started_at = datetime.now()
        country_links = self._crawl_countries()
        self.crawl_daily_report(country_links)
        self._crawl_log(started_at, "crawl_daily_table", len(country_links), status=200)


class SaveLoggerUseCase:
    def __init__(self, log_repo):
        self.log_repo = log_repo

    def save_log(self, started_at: datetime, command: str, count: int, status: int):
        l_ = LogDomain(command=command, count=count, started_at=started_at, status=status, ends_at=datetime.now())
        return self.log_repo.save(l_)


class CrawlLastStaticsUseCase(SaveLoggerUseCase):
    def __init__(self, log_repo, crawler):
        super().__init__(log_repo)
        self.crawler = crawler

    def _crawl_daily(self):
        return self.crawler.crawl_last_update()

    def execute(self):
        started_at = datetime.now()
        statics_report = StaticsDomain.from_list_dict(self._crawl_daily())
        self.save_log(started_at, "crawl_daily", len(statics_report), status=200)
        return statics_report


class CrawlYesterdayStaticUseCase(CrawlLastStaticsUseCase):
    def _crawl_daily(self):
        return self.crawler.crawl_yesterday_statics()


class SaveStaticsDailyUseCase(SaveLoggerUseCase):
    def __init__(self, log_repo, statics_repo):
        super().__init__(log_repo)
        self.statics_repo = statics_repo

    def save_daily_report(self, statics_reports):
        statics_reports = StaticsDomain.to_list_dict(statics_reports)
        self.statics_repo.insert_many(statics_reports)
        logger.debug(f"statics_reporting done,  len_values:{len(statics_reports)}  saved_at: {datetime.now()}")
        return "Done"

    def execute(self, statics_report):
        started_at = datetime.now()
        self.save_daily_report(statics_report)
        self.save_log(started_at, "save_daily_report", len(statics_report), status=200)


class UpdateCountries(SaveLoggerUseCase):
    def __init__(self, log_rep, countries_repo):
        super().__init__(log_rep)
        self.countries_repo = countries_repo

    def save_country(self, statics_reports: list):
        # statics_reports list of StaticsDomain
        # TODO : It`s not seems ok :)))
        sc_countries = {sc.country: CountryDomain.from_dict(sc.to_dict()) for sc in statics_reports}

        for country, c_domain in sc_countries.items():
            self.countries_repo.update_one(find_query={"country": country},
                                           set_=c_domain.to_dict(),
                                           upsert=True
                                           )
        return "Done"

    def execute(self, statics_report):
        started_at = datetime.now()
        self.save_country(statics_report)
        self.save_log(started_at, "save_country", len(statics_report), status=200)


class UpdateDailiesReport(SaveLoggerUseCase):
    def __init__(self, log_repo, new_case_repo, death_repo):
        super().__init__(log_repo)
        self.new_case_repo = new_case_repo
        self.death_repo = death_repo

    def update_daily_db(self, statics_report):
        for static_report in statics_report:
            self._update_new_case_daily_db(static_report)
            self._update_death_daily_db(static_report)
            logger.debug(f"update daily:{static_report.country}")
        return "done"

    @staticmethod
    def _is_need_update_last_report(last_report, report_field, new_report_time):
        if is_same_date(last_report.reported_at, new_report_time):
            if last_report.value != report_field:
                return True
        return False

    def _update_new_case_daily_db(self, country_report):
        if country_report.new_cases in ["", None, " "]:
            return None
        last_c_d = self.new_case_repo.get_last_report(country_report.country)
        new_case_cr = NewCaseDomain.from_dict(country_report.to_dict())
        new_case_cr.reported_at = new_case_cr.created_at
        logger.debug(new_case_cr.country, new_case_cr.reported_at, new_case_cr.created_at)
        if last_c_d is not None and len(last_c_d) > 0:
            last_c_d = NewCaseDomain.from_dict(last_c_d[0])

            if self._is_need_update_last_report(last_c_d, new_case_cr.new_cases, new_case_cr.reported_at):
                return self.new_case_repo.update_one_value({"_id": last_c_d._id}, new_case_cr.to_dict())

        return self.new_case_repo.insert_one(new_case_cr.to_dict())

    def _update_death_daily_db(self, country_report):
        if country_report.new_deaths in ["", None, " "]:
            return None
        last_d_d = self.death_repo.get_last_report(country_report.country)
        new_death_cr = NewDeathDomain.from_dict(country_report.to_dict())
        new_death_cr.reported_at = new_death_cr.created_at
        logger.debug(new_death_cr.country, new_death_cr.reported_at, new_death_cr.created_at)

        if last_d_d is not None and len(last_d_d) > 0:
            last_d_d = NewDeathDomain.from_dict(last_d_d[0])
            if self._is_need_update_last_report(last_d_d, new_death_cr.new_deaths, new_death_cr.reported_at):
                return self.death_repo.update_one_value({"_id": last_d_d._id}, new_death_cr.to_dict())

        return self.death_repo.insert_one(new_death_cr.to_dict())

    def execute(self, statics_report):
        started_at = datetime.now()
        self.update_daily_db(statics_report)
        self.save_log(started_at, "update_dailies", len(statics_report), status=200)


class UpdateLatestStaticsUseCase:
    def __init__(self, crawler, log_repo, statics_repo, countries_repo, new_case_repo, death_repo):
        self.crawler = crawler
        self.log_repo = log_repo
        self.statics_repo = statics_repo
        self.countries_repo = countries_repo
        self.new_case_repo = new_case_repo
        self.death_repo = death_repo

    @staticmethod
    def _change_datetime(statics_reports):
        for sr in statics_reports:
            tmp_date = datetime.now() - timedelta(days=1)
            yesterday_datetime = datetime(tmp_date.year, tmp_date.month, tmp_date.day, 23, 55, 59)
            sr.created_at = yesterday_datetime
            sr.updated_at = yesterday_datetime
        return statics_reports

    def execute(self, yesterday=False):
        crawl_last_statics = CrawlLastStaticsUseCase(self.log_repo, self.crawler)
        crawl_yesterday_statics = CrawlYesterdayStaticUseCase(self.log_repo, self.crawler)
        save_daily_statics = SaveStaticsDailyUseCase(self.log_repo, self.statics_repo)
        update_country = UpdateCountries(self.log_repo, self.countries_repo)
        update_dailies_report = UpdateDailiesReport(self.log_repo, self.new_case_repo, self.death_repo)
        if yesterday:
            statics_reports = crawl_yesterday_statics.execute()
            statics_reports = self._change_datetime(statics_reports)
        else:
            statics_reports = crawl_last_statics.execute()

        save_daily_statics.execute(statics_reports)
        update_country.execute(statics_reports)
        update_dailies_report.execute(statics_reports)
        return f"{len(statics_reports)} updated"
