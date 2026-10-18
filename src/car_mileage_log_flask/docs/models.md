# JobSite

## Fields
- name: string
- address: string required

# DriveLog

## Fields
- started_at: datetime required unique
- start_km: integer required
- end_km: integer optional
- job_site: JobSite required
- status: enum required
    - in_progress
    - completed

## Rules
1. end_km must be greater than or equal to start_km for the same drive log
2. start_km must be greater than or equal to the previous completed drive log's end_km
3. only one drive log may be in_progress at a time
4. completed drive logs should have end_km
5. in_progress drive logs may have no end_km
6. New drive logs must start strictly after the latest existing drive log.
7. Backdated insertion between existing drive logs is not allowed.
