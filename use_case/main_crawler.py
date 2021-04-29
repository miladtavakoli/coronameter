from datetime import datetime

from domain.country_domain import CountryDomain
from domain.log_domain import Log as LogDomain
from domain.newcases_domain import NewCaseDomain
from domain.newdeaths_domain import NewDeathDomain
from domain.statics_daily import StaticsDomain
from crawl.crawl_graph import CrawlDailyStatics
from crawl.crawl_daily_table import CrawlWorldMeter
from corona_meter_logger import logger
from repository.countries import CountriesRepository
from repository.death_daily import DeathReportRepository
from repository.log_repo import CrawlerLogRepository
from repository.newcase_daily import CaseReportRepository
from repository.statics_daily_log import StaticsRepository
from tools import is_same_date


class UpdateDailyUseCase:
    def __init__(self):
        self.crawl_daily_cls = CrawlWorldMeter()
        self.statics_repo = StaticsRepository()
        self.case_repo = CaseReportRepository()
        self.death_repo = DeathReportRepository()
        self.log_repo = CrawlerLogRepository()
        self.countries_repo = CountriesRepository()

    def crawl_daily(self):
        return self.crawl_daily_cls.crawl_last_update()

    def save_daily_report(self, statics_reports):
        statics_reports = [statics_report.to_dict() for statics_report in statics_reports]
        self.statics_repo.insert_many(statics_reports)
        logger.debug(f"statics_reporting done,"
                     f" len_values:{len(statics_reports)}"
                     f" saved_at: {datetime.now()}")
        return "Done"

    def save_country(self, statics_reports: list):
        # statics_reports list of StaticsDomain
        sc_countries = {sc.country: CountryDomain.from_dict(sc.to_dict()) for sc in statics_reports}

        for country, c_domain in sc_countries.items():
            self.countries_repo.update_one(find_query={"country": country},
                                           set_=c_domain.to_dict(),
                                           set_on_insert={"created_at": datetime.now()},
                                           upsert=True
                                           )

        return "Done"

    def update_daily_db(self, statics_report):
        for static_report in statics_report:
            self._update_new_case_daily_db(static_report)
            self._update_death_daily_db(static_report)
            logger.debug(f"update daily:{static_report.country}")
        return "done"

    @staticmethod
    def _is_need_update_last_report(last_report, report_field):
        if is_same_date(last_report.reported_at, datetime.now()):
            if last_report.value != report_field:
                return True
        return False

    def _update_new_case_daily_db(self, country_report):
        if country_report.new_cases in ["", None, " ", ]:
            return None
        last_c_d = self.case_repo.get_last_report(country_report.country)
        new_case_cr = NewCaseDomain.from_dict(country_report.to_dict())

        if last_c_d is not None and len(last_c_d) > 0:
            last_c_d = NewCaseDomain.from_dict(last_c_d[0])
            if self._is_need_update_last_report(last_c_d, new_case_cr.new_cases):
                return self.case_repo.update_one_value({"_id": last_c_d._id}, new_case_cr.to_dict())

        return self.case_repo.insert_one(new_case_cr.to_dict())

    def _update_death_daily_db(self, country_report):
        if country_report.new_deaths in ["", None, " "]:
            return None
        last_d_d = self.death_repo.get_last_report(country_report.country)
        new_death_cr = NewDeathDomain.from_dict(country_report.to_dict())

        if last_d_d is not None and len(last_d_d) > 0:
            last_d_d = NewDeathDomain.from_dict(last_d_d[0])
            if self._is_need_update_last_report(last_d_d, new_death_cr.new_deaths):
                return self.death_repo.update_one_value({"_id": last_d_d._id}, new_death_cr.to_dict())

        return self.death_repo.insert_one(new_death_cr.to_dict())

    def save_log(self, started_at: datetime, command: str, count: int, status: int):
        l_ = LogDomain(command=command, count=count, started_at=started_at, status=status, ends_at=datetime.now())
        return self.log_repo.save(l_)

    def execute(self):
        started_at = datetime.now()
        statics_report = StaticsDomain.from_list_dict(self.crawl_daily())
        # save report table
        self.save_daily_report(statics_report)
        self.save_log(started_at, "update_daily_statics", len(statics_report), status=200)
        # update country table
        self.save_country(statics_report)
        self.save_log(started_at, "update_countries", len(statics_report), status=200)

        # update daily collection
        started_at = datetime.now()
        self.update_daily_db(statics_report)
        logger.info(f"update_dailies end")
        self.save_log(started_at, "update_dailies", len(statics_report), status=200)


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
