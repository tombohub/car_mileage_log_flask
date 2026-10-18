-- migrate:up

DROP VIEW IF EXISTS public.drive_logs_normalized;

ALTER TABLE public.drive_logs
ALTER COLUMN date TYPE timestamp without time zone USING date::timestamp;

ALTER TABLE public.drive_logs RENAME COLUMN date TO started_at;

-- migrate:down

ALTER TABLE public.drive_logs
ALTER COLUMN started_at TYPE date USING started_at::date;

ALTER TABLE public.drive_logs RENAME COLUMN started_at TO date;

CREATE VIEW public.drive_logs_normalized AS
SELECT
    d.id,
    d.date,
    d.start_km,
    d.end_km,
    d.status,
    js.id AS job_site_id,
    js.name AS job_site_name,
    js.address AS job_site_address
FROM public.drive_logs d
    LEFT JOIN public.job_sites js ON d.job_site_id = js.id;