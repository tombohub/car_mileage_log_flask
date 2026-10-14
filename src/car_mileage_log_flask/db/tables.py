from sqlalchemy import MetaData, Table

from car_mileage_log_flask.db.connection import engine

metadata_obj = MetaData()

job_sites_table = Table("job_sites", metadata_obj, autoload_with=engine)

drive_logs_table = Table("drive_logs", metadata_obj, autoload_with=engine)
