import datetime as dt
import os
from datetime import timedelta
from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect

from car_mileage_log_flask import commands, queries
from car_mileage_log_flask.blueprints.auth import auth_bp, login_required
from car_mileage_log_flask.db.reads import (
    drive_log_select_by_id,
    drive_log_select_earliest_in_progress,
    drive_log_select_last_completed,
    drive_logs_select_count_in_progress,
    job_site_select_most_recent,
    select_all_job_sites,
    select_completed_drive_logs,
    select_job_site_by_id,
)
from car_mileage_log_flask.db.writes import (
    EndDriveInput,
    StartDriveInput,
    delete_job_site,
    drive_log_insert,
)
from car_mileage_log_flask.db.writes import drive_log_delete as db_drive_log_delete
from car_mileage_log_flask.db.writes import end_drive as db_end_drive
from car_mileage_log_flask.db.writes import start_drive as db_start_drive
from car_mileage_log_flask.domain import DriveLogStatus

app = Flask(__name__)
secret_key = os.getenv("FLASK_SECRET_KEY")
assert secret_key
app.secret_key = secret_key
app.permanent_session_lifetime = timedelta(days=7)
csrf = CSRFProtect(app)

app.register_blueprint(auth_bp)


# ---- APP ---- #


@app.get("/")
@login_required
def home():
    return redirect(url_for("start_drive"))


@app.route("/start-drive", methods=["GET", "POST"])
@login_required
def start_drive():
    # first check if there is drive in progress
    drive_in_progress = drive_log_select_earliest_in_progress()
    if drive_in_progress:
        return redirect(url_for("end_drive", id=drive_in_progress.id))

    # get data
    today_date = dt.date.today()
    job_sites = select_all_job_sites()
    last_job_site = job_site_select_most_recent()
    previous_drive_log = drive_log_select_last_completed()

    # build a base context
    context = {
        "last_job_site": last_job_site,
        "job_sites": job_sites,
        "today_date": today_date,
        "previous_drive_log": previous_drive_log,
    }

    if request.method == "POST":
        # FORM DATA
        raw_date = request.form["date"]
        raw_start_km = request.form["start_km"]
        raw_job_site_id = request.form["job_site_id"]

        date = dt.datetime.strptime(raw_date, "%Y-%m-%d")
        start_km = int(raw_start_km)
        job_site_id = int(raw_job_site_id)

        # VALIDATION
        errors = {}

        # start_km must not be lower than previous end_km
        if previous_drive_log and start_km < previous_drive_log.end_km:
            errors["start_km"] = (
                f"Start km ({start_km}) cannot be lower than previous End km ({previous_drive_log.end_km}), cmon"
            )

        if not errors:
            input = StartDriveInput(
                date=date, start_km=start_km, job_site_id=job_site_id
            )
            db_start_drive(input=input)
            flash("Drive started", "success")
            return redirect(url_for("home"))
        else:
            context["errors"] = errors
            context["date"] = raw_date
            context["start_km"] = raw_start_km
            context["job_site_id"] = raw_job_site_id

    # if request.method is GET
    return render_template("start-drive.html", **context)


@app.route("/end-drive/<int:id>", methods=["GET", "POST"])
@login_required
def end_drive(id: int):
    # get data
    drive_log = drive_log_select_by_id(id=id)

    if drive_log is None:
        flash("Drive log doesn exist", "warning")
        return redirect(url_for("home"))

    # build base context
    context: dict[str, Any] = {"drive_log": drive_log}

    if request.method == "POST":
        # FORM DATA
        raw_end_km = request.form["end_km"]
        end_km = int(raw_end_km)

        # VALIDATIONS
        errors = {}

        # end_km cannot be lower than start_km
        if end_km < drive_log.start_km:
            errors["end_km"] = (
                f"End km ({end_km}) cannot be lower than Start km ({drive_log.start_km}))"
            )

        if not errors:
            input = EndDriveInput(id=id, end_km=end_km)
            db_end_drive(input=input)
            flash("Drive ended", "success")
            return redirect(url_for("home"))
        else:
            context["errors"] = errors
            context["end_km"] = raw_end_km
    # when request method is GET
    return render_template("end_drive.html", **context)


# ---- JOB SITES ---- #


@app.get("/job-sites")
@login_required
def job_sites_index():
    job_sites = queries.get_all_job_sites()

    context = {"job_sites": job_sites}
    return render_template("job_sites/index.html", **context)


@app.get("/job-sites/new")
@login_required
def job_sites_new():
    return render_template("job_sites/new.html")


@app.get("/job-sites/details/<int:id>")
@login_required
def job_sites_details(id: int):
    job_site = select_job_site_by_id(id=id)
    context = {"job_site": job_site}
    return render_template("job_sites/details.html", **context)


@app.post("/job-sites/new")
@login_required
def job_sites_new_submit():
    name = request.form.get("job-site-name")
    address = request.form.get("job-site-address")
    print(request.form)
    if name and address:
        input = commands.CreateJobSiteInput(name=name, address=address)
        commands.create_job_site_command(input=input)
        flash("Job site added", "success")
    else:
        flash("Jos site not added", "danger")
    return redirect(url_for("job_sites_index"))


@app.get("/job-sites/delete/<int:id>")
@login_required
def job_sites_delete(id: int):
    job_site = select_job_site_by_id(id=id)
    context = {"job_site": job_site}
    return render_template("job_sites/confirm_delete.html", **context)


@app.post("/job-sites/delete/<int:id>")
@login_required
def job_sites_delete_confirmed(id: int):
    try:
        delete_job_site(id=id)
        flash("job site deleted", "success")
    except Exception:
        flash("Cannot delete job site", "danger")
    return redirect(url_for("job_sites_index"))


@app.get("/job-sites/edit/<int:id>")
@login_required
def job_sites_edit(id: int):
    job_site = select_job_site_by_id(id=id)
    context = {"job_site": job_site}
    return render_template("job_sites/edit.html", **context)


@app.post("/job-sites/edit/<int:id>")
@login_required
def job_sites_edit_submit(id: int):
    name = request.form.get("job-site-name")
    address = request.form.get("job-site-address")
    if name and address:
        input = commands.EditJobSiteInput(id=id, name=name, address=address)
        commands.edit_job_site_command(input=input)
        flash("Job site edited.", "success")
    else:
        flash("Job site not edited", "danger")
    return redirect(url_for("job_sites_index"))


# ---- DRIVE LOGS ---- #


@app.get("/drive-logs")
@login_required
def drive_logs_index():
    drive_logs = select_completed_drive_logs()
    context = {"drive_logs": drive_logs}
    return render_template("drive_logs/index.html", **context)


@app.get("/drive-logs/new")
@login_required
def drive_logs_new():
    job_sites = select_all_job_sites()
    context = {"drive_log_statuses": DriveLogStatus, "job_sites": job_sites}
    return render_template("drive_logs/new.html", **context)


@app.post("/drive-logs/new")
@login_required
def drive_logs_new_submit():
    date = dt.datetime.strptime(request.form["drive-log-date"], "%Y-%m-%d")
    start_km = int(request.form["drive-log-start-km"])
    end_km = int(request.form["drive-log-end-km"])
    job_site_id = int(request.form["job-site-id"])

    # VALIDATIONS
    errors = {}

    # Cannot be more than 1 drive in progress
    drive_in_progress_count = drive_logs_select_count_in_progress()

    drive_log_insert(
        date=date,
        start_km=start_km,
        end_km=end_km,
        status=DriveLogStatus.COMPLETED.value,
        job_site_id=job_site_id,
    )
    return redirect(url_for("drive_logs_index"))


@app.get("/drive-logs/delete/<int:id>")
@login_required
def drive_logs_delete(id: int):
    drive_log = drive_log_select_by_id(id=id)
    if drive_log is None:
        flash("Drive log doesn't exist", "warning")
        return redirect(url_for("drive_logs_index"))

    context = {"drive_log": drive_log}
    return render_template("drive_logs/delete.html", **context)


@app.post("/drive-logs/delete/<int:id>")
@login_required
def drive_logs_delete_confirmed(id: int):
    try:
        db_drive_log_delete(id=id)
        flash("Drive log deleted", "success")
    except Exception:
        flash("Drive log cannot be deleted", "danger")

    return redirect(url_for("drive_logs_index"))


@app.get("/drive-logs/edit/<int:id>")
@login_required
def drive_logs_edit(id: int):
    return render_template("drive_logs/edit.html")
