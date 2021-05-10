import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from domain.country_domain import CountryDomain
from domain.newcases_domain import NewCaseDomain
from domain.newdeaths_domain import NewDeathDomain


class CreateCountryStaticsPlotUseCase:
    def __init__(self, new_case_repo, death_repo):
        self.new_case_repo = new_case_repo
        self.death_repo = death_repo

    @staticmethod
    def _validate(res_new_case, res_death):
        if len(res_new_case) == 0 and len(res_death) == 0:
            raise ValueError("There is no data for your requested country")
        return res_new_case, res_death

    def _collect_data(self, country, d_from_day):
        res_new_case = self.new_case_repo.get_country_days_ago(country=country, from_day=d_from_day)
        res_death = self.death_repo.get_country_days_ago(country, from_day=d_from_day)
        res_new_case = NewCaseDomain.from_list_dict(res_new_case)
        res_death = NewDeathDomain.from_list_dict(res_death)
        return res_new_case, res_death

    @staticmethod
    def _convert_datetime(from_days: int):
        print(from_days)
        n = datetime.now() - timedelta(days=from_days)
        return datetime(n.year, n.month, n.day, 00, 00)

    @staticmethod
    def _draw_graph(dates_death, deaths, dates_new_case, new_cases, graph_title, file_name):
        fig, axis = plt.subplots(2, constrained_layout=True)
        axis[0].set_title(graph_title, pad=20)
        axis[0].tick_params(labelrotation=90, gridOn=True)
        axis[1].tick_params(labelrotation=90, gridOn=True)
        if dates_death is not None or deaths is not None:
            axis[0].bar(dates_death, deaths,
                        color="pink", edgecolor="black", width=0.9)
        if dates_new_case is not None or new_cases is not None:
            axis[1].bar(dates_new_case, new_cases,
                        color=mcolors.CSS4_COLORS.get("khaki", "red"), edgecolor="black", width=0.9)
        axis[0].set_ylabel("DEATH")
        axis[1].set_ylabel("NEW CASE")
        axis[0].set_xlabel("DATE")
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(f'./graph/{file_name}.png', dpi=100)

    def execute(self, country, from_days):
        dates_new_case, new_cases, deaths, dates_death = [], [], [], []
        d_from_day = self._convert_datetime(from_days)
        try:
            res_new_case, res_death = self._collect_data(country, d_from_day)
            res_new_case, res_death = self._validate(res_new_case, res_death)
        except ValueError as e:
            return e

        if res_new_case is not None:
            for rnc in res_new_case:
                dates_new_case.append(rnc.reported_at.strftime("%Y-%m-%d"))
                new_cases.append(rnc.new_cases)

        if res_death is not None:
            for rd in res_death:
                dates_death.append(rd.reported_at.strftime("%Y-%m-%d"))
                deaths.append(rd.new_deaths)

        graph_title = f'{country.title()} - {from_days} days ago'
        file_name = f'{datetime.now().date()}_{country.lower()}'
        self._draw_graph(dates_death, deaths, dates_new_case, new_cases, graph_title, file_name)
        # plt.show()


class CreateComparisonPlotUseCase:
    def __init__(self, country_repo, new_case_repo, death_repo):
        self.list_of_countries = None
        self.country_repo = country_repo
        self.new_case_repo = new_case_repo
        self.death_repo = death_repo

    @staticmethod
    def _convert_datetime(from_days: int):
        n = datetime.now() - timedelta(days=from_days)
        return datetime(n.year, n.month, n.day, 00, 00)

    @staticmethod
    def _convert_datetime(from_days: int):
        n = datetime.now() - timedelta(days=from_days)
        return datetime(n.year, n.month, n.day, 00, 00)

    def _list_of_country_name(self, first_country, second_country):
        res = self.country_repo.find_countries([first_country, second_country])
        if len(res) != 2:
            raise ValueError("There is no data for one or two countries.")
        countries = CountryDomain.from_list_dict(res)
        self.list_of_countries = [c.country for c in countries]
        return self.list_of_countries

    def _group_statics_by_country(self, statics):
        result = {c: {} for c in self.list_of_countries}
        for s in statics:
            if "new_case_per_pop" in s:
                result[s["country"]].update(
                    {s["reported_at"].strftime("%Y-%m-%d"): s["new_case_per_pop"]}
                )

            if "new_deaths_per_pop" in s:
                result[s["country"]].update(
                    {s["reported_at"].strftime("%Y-%m-%d"): s["new_deaths_per_pop"]}
                )
        return result

    def intersection_values(self, statics):
        first_static = statics[self.list_of_countries[0]]
        sec_static = statics[self.list_of_countries[1]]
        first_as_set = set(first_static.keys())
        intersection_dates = first_as_set.intersection(sec_static.keys())
        intersection_dates = sorted(intersection_dates)
        r1, r2 = {}, {}
        for int_d in intersection_dates:
            r1[int_d] = first_static[int_d]
            r2[int_d] = sec_static[int_d]

        if len(r1) == 0 or len(r2) == 0:
            raise ValueError("There is not enough data for one or two countries.")
        return {self.list_of_countries[0]: r1, self.list_of_countries[1]: r2}

    @staticmethod
    def _draw_graph(dates_death, first_death, sec_death,
                    dates_new_case, first_new_case, sec_new_case,
                    graph_title, list_of_country):
        fig, axis = plt.subplots(2, constrained_layout=True)
        axis[0].set_title(graph_title, pad=20)
        axis[0].tick_params(labelrotation=90, gridOn=True)
        axis[1].tick_params(labelrotation=90, gridOn=True)

        if dates_death is not None or first_death is not None or sec_death is not None:
            try:
                ind = np.arange(len(dates_death))
                width = 0.35
                axis[0].bar(ind - width / 2, first_death, width,
                            color=mcolors.CSS4_COLORS.get("salmon"), edgecolor=mcolors.CSS4_COLORS.get("darkred"),
                            label=list_of_country[0])
                axis[0].bar(ind + width / 2, sec_death, width,
                            color=mcolors.CSS4_COLORS.get("maroon"), edgecolor=mcolors.CSS4_COLORS.get("darkred"),
                            label=list_of_country[1])
                axis[0].set_xticks(ind)
                axis[0].set_xticklabels(dates_death)
                axis[0].legend()
            except ValueError as e:
                raise e

        if dates_new_case is not None or first_new_case is not None or sec_new_case is not None:
            try:
                ind = np.arange(len(dates_new_case))
                width = 0.35
                axis[1].bar(ind - width / 2, first_new_case, width,
                            color=mcolors.CSS4_COLORS.get("moccasin"),
                            edgecolor=mcolors.CSS4_COLORS.get("darkgoldenrod"),
                            label=list_of_country[0])
                axis[1].bar(ind + width / 2, sec_new_case, width,
                            color=mcolors.CSS4_COLORS.get("goldenrod"),
                            edgecolor=mcolors.CSS4_COLORS.get("darkgoldenrod"),
                            label=list_of_country[1])
                axis[1].set_xticks(ind)
                axis[1].set_xticklabels(dates_new_case)
                axis[1].legend()
            except ValueError as e:
                raise e

        axis[0].set_ylabel("DEATH")
        axis[1].set_ylabel("NEW CASE")
        axis[1].set_xlabel("DATE")
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(f'./graph/{datetime.now().date()}_{"-".join(list_of_country)}.png', dpi=100)

    def _separate_data(self, statics):
        s1 = statics[self.list_of_countries[0]]
        s2 = statics[self.list_of_countries[1]]
        dates = list(s1.keys())
        first_data = list(s1.values())
        sec_data = list(s2.values())
        return dates, first_data, sec_data

    def execute(self, first_country, second_country, from_days):
        d_from_days = self._convert_datetime(from_days)
        try:
            self._list_of_country_name(first_country, second_country)
        except ValueError as e:
            return f"!!! -> {e}"
        cases = self.new_case_repo.new_case_per_population([first_country, second_country], d_from_days)
        death = self.death_repo.death_per_population([first_country, second_country], d_from_days)

        try:
            grouped_cases = self.intersection_values(self._group_statics_by_country(cases))
            grouped_death = self.intersection_values(self._group_statics_by_country(death))
        except ValueError as e:
            return f"!!! -> {e}"

        dates_death, first_death, sec_death = self._separate_data(grouped_death)
        dates_new_case, first_new_case, sec_new_case = self._separate_data(grouped_cases)
        graph_title = f"compare of countries : {' - '.join(self.list_of_countries).title()}" \
                      f" from {from_days} days ago"

        try:
            self._draw_graph(
                dates_death, first_death, sec_death,
                dates_new_case, first_new_case, sec_new_case,
                graph_title=graph_title,
                list_of_country=self.list_of_countries
            )
        except ValueError as e:
            return f"!!! -> {e}"
        # plt.show()
