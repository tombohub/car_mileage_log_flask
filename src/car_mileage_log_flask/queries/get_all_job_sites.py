from car_mileage_log_flask.db.reads import select_all_job_sites
from car_mileage_log_flask.domain import JobSite


def get_all_job_sites() -> list[JobSite]:
    job_sites = select_all_job_sites()
    return job_sites
