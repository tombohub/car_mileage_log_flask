-- migrate:up

ALTER TABLE drive_log_drivelog RENAME TO drive_logs;

ALTER TABLE drive_log_jobsite RENAME TO job_sites;

-- migrate:down

ALTER TABLE job_sites RENAME TO drive_log_jobsite;

ALTER TABLE drive_logs RENAME TO drive_log_drivelog;