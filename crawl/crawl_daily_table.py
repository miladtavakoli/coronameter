import requests
from bs4 import BeautifulSoup


class CrawlWorldMeterTools:
    @staticmethod
    def _get_data(url):
        result = requests.get(url)
        return result

    @staticmethod
    def _get_tbody(table):
        return table.find_all('tbody')[0].find_all('tr')

    def _get_tds_in(self, row):
        tds = row.find_all('td')[1:]
        return self._build_list_by_content(tds, unify="body")

    def _get_thead(self, table):
        ths = table.find_all('thead')[0].find_all('tr')[0].find_all('th')[1:]
        return self._build_list_by_content(ths, unify="header")

    def _build_list_by_content(self, elements, unify=None):
        if unify == "header":
            result = [self._unify_header(elem.text) for elem in elements]
        elif unify == "body":
            result = [self._unify_body(elem.text) for elem in elements]
        else:
            result = [elem.text for elem in elements]
        return result

    def _unify_header(self, txt: str) -> str:
        # return unify header row of table
        txt = txt.lower()
        replace_cond = {
            "\n": "_",
            "/_1m": "_",
            "/1m": "_",
            "\xa0": "_",
            " ": "_",
            ",": "_",
            "new": "new_",
            "total": "total_",
            "active": "active_",
            "__": "_",
        }
        txt = self._replace_many(txt, replace_cond)
        txt = txt.replace("_", "", -1) if txt.endswith("_") else txt
        txt = txt.replace("_", "", 1) if txt.startswith("_") else txt
        txt = txt.replace("1", "one", 1) if txt.startswith("1") else txt
        txt = "country" if txt == "country_other" else txt
        return txt

    def _unify_body(self, txt):
        # return unify body rows of table
        txt = txt.lower()
        replace_cond = {
            "\n": " ",
            ",": "",
            " ": "_",
            "__": "_"
        }
        txt = self._replace_many(txt, replace_cond)
        txt = txt.replace("_", "", -1) if txt.endswith("_") else txt
        txt = txt.replace("_", "", 1) if txt.startswith("_") else txt
        txt = txt.replace("+", "", 1) if txt.startswith("+") else txt
        txt = int(txt) if txt.isdigit() else txt
        return txt

    @staticmethod
    def _replace_many(txt, replace_cond: dict) -> str:
        for old, new in replace_cond.items():
            txt = txt.replace(old, new)
        return txt

    def _find_table_by(self, url, table_id: str):
        # each table has unique id. find table with id.
        web_txt = self._get_data(url)
        soup = BeautifulSoup(web_txt.text, "html.parser")
        return soup.find(attrs={"id": table_id})

    @staticmethod
    def _find_country_link(tr):
        # second col is country name with link
        td = tr.find_all('td')
        if td[1].a is not None:
            return td[1].a.attrs['href']
        return None


class CrawlWorldMeter(CrawlWorldMeterTools):
    def __init__(self):
        # Base URL
        self.url = "https://www.worldometers.info/coronavirus/"

        # some country entered in table is not country
        self.skip_list = ("northamerica", "asia", "southamerica", "europe", "africa", "oceania", "world", "")

        # Continent skip
        self.continent = ("Europe", "North America", "Asia", "South America", "Africa", "Oceania")

    def _is_country_name_in_skip_list(self, country_name):
        return country_name in self.skip_list

    def _aggregation_table_result(self, table):
        headers = self._get_thead(table)
        headers.append("wom_link")
        trows = self._get_tbody(table)
        result = []
        for tr in trows:
            td = self._get_tds_in(tr)
            if not self._is_country_name_in_skip_list(country_name=td[0]):
                td.append(self._find_country_link(tr))
                result.append(dict(zip(headers, td)))
        return result

    def crawl_last_update(self):
        table = self._find_table_by(self.url, "main_table_countries_today")
        return self._aggregation_table_result(table)

    def crawl_yesterday_statics(self):
        table = self._find_table_by(self.url, "main_table_countries_yesterday")
        return self._aggregation_table_result(table)

    def get_country_link(self):
        table = self._find_table_by(self.url, "main_table_countries_today")
        trows = self._get_tbody(table)
        result = {}
        for tr in trows:
            td = tr.find_all('td')
            if self._unify_body(td[1].text) in self.skip_list or td is None:
                continue
            if td[1].a is not None:
                result[self._unify_body(td[1].text)] = td[1].a.attrs['href']
        return result
