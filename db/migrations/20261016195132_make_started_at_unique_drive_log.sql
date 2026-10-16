-- migrate:up
ALTER TABLE public.drive_logs
ADD CONSTRAINT drive_logs_started_at_unique UNIQUE (started_at);

-- migrate:down
ALTER TABLE public.drive_logs
DROP CONSTRAINT drive_logs_started_at_unique;