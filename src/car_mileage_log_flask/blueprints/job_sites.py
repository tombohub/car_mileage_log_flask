from flask import Blueprint, render_template, request
from car_mileage_log_flask import commands, queries
from car_mileage_log_flask.blueprints.auth import login_required
from sqlalchemy import select
from car_mileage_log_flask.db.connection import Session
from car_mileage_log_flask.db.models import JobSite

job_site_bp = Blueprint('job_sites', __name__, url_prefix='/job-sites')

@job_site_bp.get('/')
@login_required
def index():
    with Session() as session:
        stmt = select(JobSite)
        job_sites = session.scalars(stmt).all()

    return render_template('job_sites/index.html', job_sites=job_sites)
