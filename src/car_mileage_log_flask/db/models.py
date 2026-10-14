from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Identity, DateTime, Integer, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime as dt
class Base(DeclarativeBase):
    pass

class JobSite(Base):
    __tablename__ ='job_sites'

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[dt.datetime] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))

    drive_logs: Mapped[list['DriveLog']] = relationship(back_populates='job_site')


class DriveLog(Base):
    __tablename__ = 'drive_logs'
    __table_args__ = (Index("drive_log_drivelog_job_site_id_41254f97", "job_site_id"),)

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    date: Mapped[dt.date] = mapped_column(Date)
    start_km: Mapped[int] = mapped_column(Integer)
    end_km: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))

    job_site_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            'job_sites.id',
            deferrable=True,
            initially='DEFERRED',
            name='drive_log_drivelog_job_site_id_41254f97_fk_drive_log_jobsite_id'
        )
    )

    job_site: Mapped[JobSite] = relationship(
        back_populates='drive_logs'
    )