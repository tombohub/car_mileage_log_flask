import datetime as dt
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete, insert, text, update

from car_mileage_log_flask.db.connection import engine
from car_mileage_log_flask.db.models import DriveLogDrivelog
from car_mileage_log_flask.db.reads import drive_log_select_last_completed
from car_mileage_log_flask.db.tables import drive_logs_table, job_sites_table
from car_mileage_log_flask.domain import DriveLogStatus, JobSite

# --- APP --- #


@dataclass
class StartDriveInput:
    date: dt.date
    start_km: int
    job_site_id: int


def start_drive(input: StartDriveInput):
    now = dt.datetime.now(timezone.utc)
    stmt = insert(drive_logs_table).values(
        date=input.date,
        start_km=input.start_km,
        job_site_id=input.job_site_id,
        status=DriveLogStatus.IN_PROGRESS.value,
        created_at=now,
        updated_at=now,
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


@dataclass
class EndDriveInput:
    id: int
    end_km: int


def end_drive(input: EndDriveInput):
    sql = """
        UPDATE drive_log_drivelog
        SET end_km = :end_km,
            updated_at = :updated_at,
            status = :status
        WHERE id = :id;
        """
    now = dt.datetime.now(timezone.utc)
    with engine.connect() as conn:
        conn.execute(
            text(sql),
            {
                "end_km": input.end_km,
                "updated_at": now,
                "id": input.id,
                "status": DriveLogStatus.COMPLETED.value,
            },
        )
        conn.commit()


# ---- JOB SITES ---- #


def insert_job_site(job_site: JobSite):
    now = datetime.now(timezone.utc)
    stmt = insert(job_sites_table).values(
        name=job_site.name, address=job_site.address, created_at=now, updated_at=now
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def delete_job_site(id: int):
    stmt = delete(job_sites_table).where(job_sites_table.c.id == id)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def update_job_site(job_site: JobSite):
    now = datetime.now(timezone.utc)
    stmt = (
        update(job_sites_table)
        .where(job_sites_table.c.id == job_site.id)
        .values(name=job_site.name, address=job_site.address, updated_at=now)
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


# ---- DRIVE LOGS ---- #


def drive_log_insert(
    date: dt.date, start_km: int, end_km: int, status: str, job_site_id: int
):
    now = datetime.now(timezone.utc)
    stmt = insert(drive_logs_table).values(
        created_at=now,
        updated_at=now,
        date=date,
        start_km=start_km,
        end_km=end_km,
        status=status,
        job_site_id=job_site_id,
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def drive_log_delete(id: int):
    sql = """
        DELETE FROM drive_log_drivelog
        WHERE id = :id
        """
    with engine.connect() as conn:
        conn.execute(text(sql), {"id": id})
        conn.commit()
