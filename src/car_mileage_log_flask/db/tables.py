from sqlalchemy import MetaData, Table

from car_mileage_log_flask.db.connection import engine

metadata_obj = MetaData()

job_sites_table = Table("drive_log_jobsite", metadata_obj, autoload_with=engine)

drive_logs_table = Table("drive_log_drivelog", metadata_obj, autoload_with=engine)
