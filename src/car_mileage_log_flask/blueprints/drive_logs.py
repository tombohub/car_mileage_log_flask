from datetime import UTC, date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import DateField, IntegerField, SelectField, ValidationError
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
)

from car_mileage_log_flask.blueprints.auth import login_required
from car_mileage_log_flask.db.connection import Session
from car_mileage_log_flask.db.models import DriveLog, JobSite

drive_logs_bp = Blueprint("drive_logs", __name__, url_prefix="/drive-logs")


class DriveLogForm(FlaskForm):
    date = DateField("Date", default=date.today, validators=[InputRequired()])
    start_km = IntegerField(
        "Starting km odometer", validators=[InputRequired(), NumberRange(min=0)]
    )
    end_km = IntegerField(
        "Ending km odometer", validators=[Optional(), NumberRange(min=0)]
    )
    status = SelectField(
        "Status",
        validators=[DataRequired()],
        choices=[
            ("in_progress", "In progress"),
            ("completed", "Completed"),
        ],
    )
    job_site_id = SelectField("Job site", coerce=int, validators=[InputRequired()])

    def validate_end_km(self, field):
        if (
            field.data is not None
            and self.start_km.data is not None
            and field.data < self.start_km.data
        ):
            raise ValidationError("Ending km must not be lower than starting km")


@drive_logs_bp.get("/")
@login_required
def index():
    with Session() as session:
        stmt = select(DriveLog).order_by(DriveLog.created_at.desc())
        drive_logs = session.scalars(stmt).all()

    return render_template("/drive_logs/index.html", drive_logs=drive_logs)


@drive_logs_bp.get("/<int:id>")
@login_required
def details(id: int):
    with Session() as session:
        drive_log = session.get(DriveLog, id)

        if drive_log is None:
            abort(404)

    return render_template("drive_logs/details.html", drive_log=drive_log)


@drive_logs_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = DriveLogForm()

    with Session() as session:
        job_sites = session.scalars(
            select(JobSite).order_by(JobSite.address, JobSite.id)
        ).all()

        form.job_site_id.choices = [(site.id, site.address) for site in job_sites]

        if form.validate_on_submit():
            now = datetime.now(UTC)

            drive_log = DriveLog(
                date=form.date.data,
                start_km=form.start_km.data,
                end_km=form.end_km.data,
                status=form.status.data,
                job_site_id=form.job_site_id.data,
                created_at=now,
                updated_at=now,
            )

            session.add(drive_log)
            session.commit()

            flash("Drive log created", "success")
            return redirect(url_for("drive_logs.index"))

    return render_template("drive_logs/new.html", form=form)


@drive_logs_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id: int):
    with Session() as session:
        drive_log = session.get(DriveLog, id)

        if drive_log is None:
            abort(404)

        form = DriveLogForm(obj=drive_log)

        job_sites = session.scalars(select(JobSite).order_by(JobSite.created_at)).all()

        form.job_site_id.choices = [
            (site.id, site.name or site.address) for site in job_sites
        ]

        if form.validate_on_submit():
            form.populate_obj(drive_log)
            drive_log.updated_at = datetime.now(UTC)

            session.commit()

            flash("Drive log updated", "success")
            return redirect(url_for("drive_logs.index"))

        return render_template("drive_logs/edit.html", form=form, drive_log=drive_log)


@drive_logs_bp.post("<int:id>/delete")
@login_required
def delete(id: int):
    with Session() as session:
        drive_log = session.get(DriveLog, id)

        if drive_log is None:
            abort(404)

        session.delete(drive_log)
        session.commit()

    flash("Drive log deleted.", "success")
    return redirect(url_for("drive_logs.index"))
