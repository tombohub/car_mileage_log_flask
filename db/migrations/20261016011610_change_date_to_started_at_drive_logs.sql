-- migrate:up

ALTER TABLE drive_logs
ALTER COLUMN date TYPE timestamptz USING (
    date::timestamp AT TIME ZONE 'America/Toronto'
);

ALTER TABLE drive_logs RENAME COLUMN date TO started_at;

-- migrate:down

ALTER TABLE drive_logs
ALTER COLUMN started_at TYPE date USING (
    (
        started_at AT TIME ZONE 'America/Toronto'
    )::date
);

ALTER TABLE drive_logs RENAME COLUMN started_at TO date;