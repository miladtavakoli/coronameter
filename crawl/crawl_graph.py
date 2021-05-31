import collections
import time

from selenium.common.exceptions import WebDriverException
from selenium import webdriver


class CrawlDailyStatics:
    def __init__(self, link):
        self.max_retries = 5
        self.url = f"https://www.worldometers.info/coronavirus/{link}"
        options = webdriver.FirefoxOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Firefox(options=options, executable_path="./geckodriver")

    def get_data(self):
        c = 1
        while c < self.max_retries:
            try:
                return self.driver.get(self.url)
            except WebDriverException:
                time.sleep(2)
                c += 1
                continue
        return False

    def _get_charts_name(self):
        js_command = "charts=[];Highcharts.charts.forEach(element => charts.push(element.renderTo['id']));" \
                     "return charts;"
        return self.driver.execute_script(js_command)

    def _get_statics_daily(self, charts_index, key):
        js_commands_values = f"return Highcharts.charts[{charts_index}].series[0].processedYData"
        js_commands_categories = f"result=[];" \
                                 f"Highcharts.charts[{charts_index}].series[0].data.forEach(" \
                                 "element => result.push(element.category));" \
                                 "return result;"

        result = []
        counter = 0
        while self.max_retries > counter:
            values = self.driver.execute_script(js_commands_values)
            categories = self.driver.execute_script(js_commands_categories)
            if len(values) == len(categories):
                for index in range(len(values)):
                    result.append({"reported_at": categories[index], key: values[index]})
                break

            else:
                counter += 1
        return result

    @staticmethod
    def _get_index_death_daily(charts_name):
        try:
            return charts_name.index("graph-deaths-daily")
        except ValueError:
            return None

    @staticmethod
    def _get_index_case_daily(charts_name):
        try:
            return charts_name.index("graph-cases-daily")
        except ValueError:
            return None

    def execute(self):
        if self.get_data() is False:
            self.driver.close()
            raise ValueError(f"Load{self.url} is failed")

        charts_name = self._get_charts_name()
        death_daily_index = self._get_index_death_daily(charts_name)
        case_daily_index = self._get_index_case_daily(charts_name)

        death_daily = self._get_statics_daily(death_daily_index,
                                              key='new_deaths') if death_daily_index is not None else None
        case_daily = self._get_statics_daily(case_daily_index,
                                             key='new_cases') if case_daily_index is not None else None

        self.driver.close()
        result_graph = collections.namedtuple('result_graph', ['death_daily', 'case_daily'])
        return result_graph(death_daily, case_daily)
