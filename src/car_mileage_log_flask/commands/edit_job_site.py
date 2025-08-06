from dataclasses import dataclass

from car_mileage_log_flask.db.writes import update_job_site
from car_mileage_log_flask.domain import JobSite


@dataclass
class EditJobSiteInput:
    id: int
    name: str
    address: str


def edit_job_site_command(input: EditJobSiteInput):
    job_site = JobSite(id=input.id, name=input.name, address=input.address)
    update_job_site(job_site=job_site)
