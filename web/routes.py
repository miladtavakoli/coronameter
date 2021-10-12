from flask import Blueprint, jsonify, request

from domain.country_domain import CountryDomain
from repository.countries import CountriesRepository
from repository.death_daily import DeathReportRepository
from repository.newcase_daily import CaseReportRepository
from use_case import country_usecase
from use_case.country_usecase import CountryDetail

base_bp = Blueprint("base_bp", __name__, )


@base_bp.route("/countries", methods=["GET"])
def countries():
    use_case = country_usecase.CountryList(CountriesRepository(), CountryDomain())
    res = use_case.execute()
    result = {k: v for r in res for k, v in r.items()}
    return jsonify(result)


@base_bp.route("/countries/<string:country>", methods=["GET"])
def get_country(country="iran"):
    how_many_days_ago = request.args.get("days")
    if how_many_days_ago is None:
        how_many_days_ago = 20
    how_many_days_ago = int(how_many_days_ago)
    use_case = CountryDetail(country_repo=CountriesRepository(),
                             new_case_repo=CaseReportRepository(),
                             death_repo=DeathReportRepository())
    result = use_case.execute(country, how_many_days_ago)
    return jsonify(result)
