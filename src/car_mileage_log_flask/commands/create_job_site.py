from dataclasses import dataclass

from car_mileage_log_flask.db.writes import insert_job_site
from car_mileage_log_flask.domain import JobSite


@dataclass
class CreateJobSiteInput:
    name: str
    address: str


def create_job_site_command(input: CreateJobSiteInput):
    job_site = JobSite(id=None, name=input.name, address=input.address)
    insert_job_site(job_site=job_site)
