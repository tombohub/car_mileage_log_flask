from datetime import UTC, datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import StringField
from wtforms.validators import DataRequired

from car_mileage_log_flask.blueprints.auth import login_required
from car_mileage_log_flask.db.connection import Session
from car_mileage_log_flask.db.models import JobSite

job_site_bp = Blueprint("job_sites", __name__, url_prefix="/job-sites")


class JobSiteForm(FlaskForm):
    name = StringField("Name")
    address = StringField("Address", validators=[DataRequired()])


@job_site_bp.get("/")
@login_required
def index():
    with Session() as session:
        stmt = select(JobSite)
        job_sites = session.scalars(stmt).all()

    return render_template("job_sites/index.html", job_sites=job_sites)


@job_site_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = JobSiteForm()

    if form.validate_on_submit():
        now = datetime.now(timezone.utc)

        job_site = JobSite(
            name=form.name.data,
            address=form.address.data,
            created_at=now,
            updated_at=now,
        )

        with Session() as session:
            session.add(job_site)
            session.commit()

        flash("Job site added", "success")

        return redirect(url_for("job_sites.index"))

    return render_template("job_sites/new.html", form=form)


@job_site_bp.get("/<int:id>")
@login_required
def details(id: int):
    with Session() as session:
        job_site = session.get(JobSite, id)

        if job_site is None:
            abort(404)

        return render_template("job_sites/details.html", job_site=job_site)


@job_site_bp.route("<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id: int):
    with Session() as session:
        job_site = session.get(JobSite, id)

        if job_site is None:
            abort(404)

        form = JobSiteForm(obj=job_site)

        if form.validate_on_submit():
            job_site.name = form.name.data  # type: ignore
            job_site.address = form.address.data  # type: ignore
            job_site.updated_at = datetime.now(UTC)

            session.commit()

            flash("Job site updated", "success")

            return redirect(url_for("job_sites.index"))

        return render_template("job_sites/edit.html", form=form, job_site=job_site)


@job_site_bp.post("/<int:id>/delete")
@login_required
def delete(id: int):
    with Session() as session:
        job_site = session.get(JobSite, id)

        if job_site is None:
            abort(404)

        if job_site.drive_logs:
            flash("This job site has driving logs attached. Cannot delete", "warning")
            return redirect(url_for("job_sites.index"))

        session.delete(job_site)
        session.commit()

    flash("Job site deleted", "success")

    return redirect(url_for("job_sites.index"))
