import datetime as dt
from dataclasses import dataclass

from sqlalchemy import bindparam, desc, select, text

from car_mileage_log_flask.db.connection import db, engine
from car_mileage_log_flask.db.tables import drive_logs_table, job_sites_table
from car_mileage_log_flask.domain import DriveLogStatus, JobSite

# --- JOB SITES --- #


def select_all_job_sites() -> list[JobSite]:
    stmt = select(job_sites_table)
    with engine.connect() as conn:
        result = conn.execute(stmt)

    job_sites = [
        JobSite(id=row["id"], name=row["name"], address=row["address"])
        for row in result.mappings()
    ]
    return job_sites


def select_job_site_by_id(id: int) -> JobSite:
    stmt = select(job_sites_table).where(job_sites_table.c.id == id)
    with engine.connect() as conn:
        result = conn.execute(stmt)

    row = result.mappings().one()
    return JobSite(id=row["id"], name=row["name"], address=row["address"])


def job_site_select_most_recent() -> JobSite | None:
    stmt = (
        select(
            drive_logs_table.c.job_site_id,
            job_sites_table.c.address.label("job_site_address"),
            job_sites_table.c.name.label("job_site_name"),
        )
        .join(job_sites_table)
        .order_by(desc(drive_logs_table.c.created_at))
        .limit(bindparam("limit"))
    )

    with engine.connect() as conn:
        result = conn.execute(stmt, {"limit": 1})

    row = result.mappings().first()

    if row is None:
        return None

    return JobSite(
        id=row["job_site_id"],
        address=row["job_site_address"],
        name=row["job_site_name"],
    )


# ---- DRIVE LOGS ---- #


@dataclass
class DriveLog:
    id: int
    date: dt.date
    start_km: int
    end_km: int | None
    status: str
    job_site_id: int
    job_site_name: str
    job_site_address: str


@dataclass
class DriveLogCompleted:
    id: int
    date: dt.date
    start_km: int
    end_km: int
    status: str
    job_site_id: int
    job_site_name: str
    job_site_address: str


def select_completed_drive_logs() -> list[DriveLogCompleted]:
    stmt = (
        select(
            drive_logs_table.c.id,
            drive_logs_table.c.date,
            drive_logs_table.c.start_km,
            drive_logs_table.c.end_km,
            drive_logs_table.c.status,
            drive_logs_table.c.job_site_id,
            job_sites_table.c.name.label("job_site_name"),
            job_sites_table.c.address.label("job_site_address"),
        )
        .join(job_sites_table)
        .where(drive_logs_table.c.status == DriveLogStatus.COMPLETED.value)
        .order_by(drive_logs_table.c.created_at.desc())
    )

    with engine.connect() as conn:
        result = conn.execute(stmt)

    drive_logs = [
        DriveLogCompleted(
            id=row["id"],
            date=row["date"],
            start_km=row["start_km"],
            end_km=row["end_km"],
            status=row["status"],
            job_site_id=row["job_site_id"],
            job_site_name=row["job_site_name"],
            job_site_address=row["job_site_address"],
        )
        for row in result.mappings()
    ]
    return drive_logs


def drive_log_select_earliest_in_progress() -> DriveLogCompleted | None:
    sql = """
            SELECT d.*, j.name AS job_site_name, j.address as job_site_address
            FROM drive_log_drivelog d
            JOIN drive_log_jobsite j ON d.job_site_id = j.id
            WHERE status = 'in_progress'
            ORDER BY created_at ASC
            LIMIT 1;
        """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        row = result.mappings().first()

    if row is None:
        return None

    return DriveLogCompleted(
        id=row["id"],
        date=row["date"],
        start_km=row["start_km"],
        end_km=row["end_km"],
        status=row["status"],
        job_site_id=row["job_site_id"],
        job_site_name=row["job_site_name"],
        job_site_address=row["job_site_address"],
    )


def drive_log_select_last_completed() -> DriveLogCompleted | None:
    sql = """
        SELECT d.*, j.name AS job_site_name, j.address as job_site_address
        FROM drive_log_drivelog d
        JOIN drive_log_jobsite j ON d.job_site_id = j.id
        ORDER BY created_at DESC
        LIMIT 1;
        """
    with engine.connect() as conn:
        res = conn.execute(text(sql))
        row = res.mappings().first()

    if row is None:
        return None

    return DriveLogCompleted(
        id=row["id"],
        date=row["date"],
        start_km=row["start_km"],
        end_km=row["end_km"],
        status=row["status"],
        job_site_id=row["job_site_id"],
        job_site_name=row["job_site_name"],
        job_site_address=row["job_site_address"],
    )


def drive_log_select_by_id(id: int) -> DriveLog | None:
    sql = """
        SELECT d.*, j.name AS job_site_name, j.address as job_site_address
        FROM drive_log_drivelog d
        JOIN drive_log_jobsite j ON d.job_site_id = j.id
        WHERE d.id = :id
        LIMIT 1;
        """

    with engine.connect() as conn:
        result = conn.execute(text(sql), {"id": id})
        row = result.mappings().first()

    if row is None:
        return None

    return DriveLog(
        id=row["id"],
        date=row["date"],
        start_km=row["start_km"],
        end_km=row["end_km"],
        status=row["status"],
        job_site_id=row["job_site_id"],
        job_site_name=row["job_site_name"],
        job_site_address=row["job_site_address"],
    )


def drive_logs_select_count_in_progress():
    sql = """
            SELECT count(*)
            FROM drive_log_drivelog
            WHERE status = 'in_progress';
            """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        count = result.scalar() or 0

    return int(count)
