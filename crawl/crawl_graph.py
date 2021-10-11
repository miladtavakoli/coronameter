import collections
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from config import CRAWLER_CONFIG


class CrawlDailyStatics:
    def __init__(self, link):
        self.max_retry = CRAWLER_CONFIG["MAX_RETRY"]
        self.sleep_time = CRAWLER_CONFIG["SLEEP_TIME"]
        self.url = f"https://www.worldometers.info/coronavirus/{link}"
        options = webdriver.FirefoxOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Firefox(options=options, executable_path="./geckodriver")

    def get_data(self):
        for count_try in range(self.max_retry):
            try:
                return self.driver.get(self.url), True
            except WebDriverException:
                time.sleep(self.sleep_time)
                continue
        return None, False

    def _get_charts_name(self) -> list:
        # Find list of Highcharts in graph page by execute js command
        # SAMPLE:
        # [ "deaths-cured-outcome-small", "coronavirus-cases-linear", "coronavirus-cases-log",.....]
        js_command = "charts=[];Highcharts.charts.forEach(element => charts.push(element.renderTo['id']));" \
                     "return charts;"
        return self.driver.execute_script(js_command)

    def _get_statics_daily(self, charts_index, category_name):
        # Values of table
        # [0, 0, 0, 0, 0,....]
        js_commands_values = f"return Highcharts.charts[{charts_index}].series[0].processedYData"

        # DATES dates of table
        # [ "Feb 15, 2020", "Feb 16, 2020",....]
        js_commands_dates = f"result=[];" \
                                 f"Highcharts.charts[{charts_index}].series[0].data.forEach(" \
                                 "element => result.push(element.category));" \
                                 "return result;"

        result = []
        for _ in range(self.max_retry):
            values = self.driver.execute_script(js_commands_values)
            categories = self.driver.execute_script(js_commands_dates)
            if len(values) == len(categories):
                for index in range(len(values)):
                    result.append({"reported_at": categories[index],
                                   category_name: values[index]})
                break
        return result

    @staticmethod
    def _get_index_death_daily_chart(charts_name: list):
        try:
            return charts_name.index("graph-deaths-daily")
        except ValueError:
            return

    @staticmethod
    def _get_index_case_daily_chart(charts_name: list):
        try:
            return charts_name.index("graph-cases-daily")
        except ValueError:
            return

    def execute(self):
        data, is_valid = self.get_data()
        if not is_valid:
            self.driver.close()
            raise ValueError(f"Load {self.url} failed !!!")

        charts_name = self._get_charts_name()
        death_daily_index = self._get_index_death_daily_chart(charts_name)
        case_daily_index = self._get_index_case_daily_chart(charts_name)

        death_daily = self._get_statics_daily(death_daily_index,
                                              category_name='new_deaths') if death_daily_index is not None else None
        case_daily = self._get_statics_daily(case_daily_index,
                                             category_name='new_cases') if case_daily_index is not None else None

        self.driver.close()
        result_graph = collections.namedtuple('result_graph', ['death_daily', 'case_daily'])
        return result_graph(death_daily, case_daily)
