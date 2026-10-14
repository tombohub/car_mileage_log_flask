# JobSite

## Fields
- name: string
- address: string required

# DriveLog

## Fields
- date: date required
- start_km: integer required
- end_km: integer optional
- job_site: JobSite required
- status: enum required
    - in_progress
    - completed

## Rules
- end_km must be greater than or equal to start_km for the same drive log
- start_km must be greater than or equal to the previous completed drive log's end_km
- only one drive log may be in_progress at a time
- completed drive logs should have end_km
- in_progress drive logs may have no end_km
