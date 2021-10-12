from datetime import datetime, timedelta


class CountryList:
    def __init__(self, repo, domain):
        self.repo = repo
        self.domain = domain

    @staticmethod
    def convert_name_to_title(name):
        return name.replace("_", " ").title()

    def execute(self):
        res = self.repo.country_list()
        res = self.domain.to_list_dict(res)
        res = [{item['_id']: self.convert_name_to_title(item['_id'])} for item in res]
        return res


class CountryDetail:
    def __init__(self, country_repo, death_repo, new_case_repo):
        self.country_repo = country_repo
        self.death_repo = death_repo
        self.new_case_repo = new_case_repo

    @staticmethod
    def _check_output(res_new_case, res_death):
        if len(res_new_case) == 0 and len(res_death) == 0:
            raise ValueError("There is no data for your requested country")

    def _collect_data(self, country, d_from_day):
        res_country = self.country_repo.find_one({"country": country})
        new_case_project = {"_id": 0, "reported_at": 1, "new_cases": 1}
        death_project = {"_id": 0, "reported_at": 1, "new_deaths": 1}
        res_new_case = self.new_case_repo.get_country_days_ago_projects(country=country, from_day=d_from_day,
                                                                        project=new_case_project)
        res_death = self.death_repo.get_country_days_ago_projects(country=country, from_day=d_from_day,
                                                                  project=death_project)
        return res_new_case, res_death, res_country

    @staticmethod
    def _convert_datetime(from_days: int):
        n = datetime.now() - timedelta(days=from_days)
        return datetime(n.year, n.month, n.day, 00, 00)

    @staticmethod
    def calculate_total(new_case, new_death):
        total_death, total_cases = 0, 0
        for d in new_death:
            total_death += d.get("new_deaths", 0)
        for c in new_case:
            total_cases += c.get("new_cases", 0)
        return total_death, total_cases

    def execute(self, country, from_days):
        datetime_from_day = self._convert_datetime(from_days)
        res_new_case, res_death, res_country = self._collect_data(country, datetime_from_day)
        self._check_output(res_new_case, res_death)
        total_death, total_new_case = self.calculate_total(res_new_case, res_death)
        result = {"country": res_country,
                  "new_cases": res_new_case,
                  "deaths": res_death,
                  "total_new_case": total_new_case,
                  "total_death": total_death}
        return result
