import datetime as dt
import os
from datetime import timedelta
from typing import Any

from flask import (
    Flask,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from pyinstrument import Profiler

from car_mileage_log_flask.blueprints.auth import auth_bp, login_required
from car_mileage_log_flask.blueprints.drive_logs import drive_logs_bp
from car_mileage_log_flask.blueprints.job_sites import job_site_bp
from car_mileage_log_flask.db.reads import (
    drive_log_select_by_id,
    drive_log_select_earliest_in_progress,
    drive_log_select_last_completed,
    drive_logs_select_count_in_progress,
    job_site_select_most_recent,
    select_all_job_sites,
)
from car_mileage_log_flask.db.writes import (
    EndDriveInput,
    StartDriveInput,
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
bootstrap = Bootstrap5(app)

app.register_blueprint(auth_bp)
app.register_blueprint(job_site_bp)
app.register_blueprint(drive_logs_bp)


# ---------------------------------- SIGNALS --------------------------------- #


@app.before_request
def before_request():
    if "profile" in request.args:
        g.profiler = Profiler()
        g.profiler.start()


@app.after_request
def after_request(response):
    if not hasattr(g, "profiler"):
        return response
    g.profiler.stop()
    output_html = g.profiler.output_html()
    return make_response(output_html)


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
    job_sites = select_all_job_sites()
    last_job_site = job_site_select_most_recent()
    previous_drive_log = drive_log_select_last_completed()

    # build a base context
    context = {
        "last_job_site": last_job_site,
        "job_sites": job_sites,
        "started_at": "",
        "previous_drive_log": previous_drive_log,
    }

    if request.method == "POST":
        # FORM DATA
        raw_started_at = request.form.get("started_at", "")
        raw_start_km = request.form["start_km"]
        raw_job_site_id = request.form["job_site_id"]

        start_km = int(raw_start_km)
        job_site_id = int(raw_job_site_id)

        # VALIDATION
        errors = {}

        try:
            started_at = dt.datetime.strptime(raw_started_at, "%Y-%m-%dT%H:%M")
        except ValueError:
            errors["started_at"] = "Enter a valid start date and time."

        # start_km must not be lower than previous end_km
        if previous_drive_log and start_km < previous_drive_log.end_km:
            errors["start_km"] = (
                f"Start km ({start_km}) cannot be lower than previous End km ({previous_drive_log.end_km}), cmon"
            )

        if not errors:
            input = StartDriveInput(
                started_at=started_at, start_km=start_km, job_site_id=job_site_id
            )
            db_start_drive(input=input)
            flash("Drive started", "success")
            return redirect(url_for("home"))
        else:
            context["errors"] = errors
            context["started_at"] = raw_started_at
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
