from typing import List, Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship
import datetime

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class DriveLogJobsite(Base):
    __tablename__ = 'drive_log_jobsite'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='drive_log_jobsite_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))

    drive_log_drivelog: Mapped[List['DriveLogDrivelog']] = relationship('DriveLogDrivelog', back_populates='job_site')


class DriveLogDrivelog(Base):
    __tablename__ = 'drive_log_drivelog'
    __table_args__ = (
        ForeignKeyConstraint(['job_site_id'], ['drive_log_jobsite.id'], deferrable=True, initially='DEFERRED', name='drive_log_drivelog_job_site_id_41254f97_fk_drive_log_jobsite_id'),
        PrimaryKeyConstraint('id', name='drive_log_drivelog_pkey'),
        Index('drive_log_drivelog_job_site_id_41254f97', 'job_site_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    date: Mapped[datetime.date] = mapped_column(Date)
    start_km: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    job_site_id: Mapped[int] = mapped_column(BigInteger)
    end_km: Mapped[Optional[int]] = mapped_column(Integer)

    job_site: Mapped['DriveLogJobsite'] = relationship('DriveLogJobsite', back_populates='drive_log_drivelog')
