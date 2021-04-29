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
