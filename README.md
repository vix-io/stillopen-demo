# AI remote job finder, powered by StillOpen

[![mcptry](https://mcptry.com/badge/work.stillopen/jobs)](https://mcptry.com/servers/work.stillopen/jobs)

A small, dependency-free Python example of the [StillOpen](https://stillopen.work)
API: search fully-remote jobs, re-check each one in a single batch call, and
print **the evidence that it is still open** — not just the listing.

Most job data goes stale silently. StillOpen re-reads every listing against
the employer's own applicant tracking system (ATS: Greenhouse, Lever, Ashby,
Workable, Workday…) and expires it when the employer takes it down. Every
record says how it was checked and when.

```
$ python find_jobs.py python --loc de --level senior --limit 3
220 matches; showing 3.

Senior Backend Engineer (Python) - AI — SplitMetrics
  Spain, Europe, Portugal
  still open: re-checked against the employer's ATS, 2026-11-15 18:22 UTC
  https://stillopen.work/job/384447-splitmetrics-senior-backend-engineer-python-ai
...
Data provided by StillOpen — https://stillopen.work
```

## Run it

Python 3.9+, standard library only, no API key.

```bash
python find_jobs.py "data engineer" --loc emea
python find_jobs.py --area design --level senior --loc worldwide
python find_jobs.py --verify https://job-boards.greenhouse.io/acme/jobs/123
```

`--loc` takes a country code (`de`), a region (`emea`) or `worldwide`. A
country means "can I apply from here", so it includes roles open across a
region that contains it.

## What it calls

| Endpoint | Used for |
|---|---|
| `GET /api/v1/jobs` | search, up to 20 per call, cursor paging |
| `POST /api/v1/jobs/status` | re-check many ids you already hold in one call |
| `GET /api/v1/jobs/verify?url=` | ask about any job URL (20 a day free) |

`evidence_type` is the field to read: `ats_verified` means the employer's own
ATS was re-read and still lists the posting. A closed listing comes back with
`closure: observed` when we saw the employer remove it. Full field reference:
[stillopen.work/llms.txt](https://stillopen.work/llms.txt) and
[stillopen.work/agents](https://stillopen.work/agents).

## For AI assistants

The same data is an MCP server at `https://stillopen.work/api/v1/mcp` (tools
`search_jobs`, `get_job`, `check_job_status`, `verify_job`,
`get_company_stats`) and an A2A agent. Read-only, no key.

## Terms

The API is free within its published rate limits. Wherever you show StillOpen
data, show **"Data provided by StillOpen"** linked to https://stillopen.work and
link each listing to its `canonical_url`. See
[stillopen.work/api-terms](https://stillopen.work/api-terms).

This example is MIT licensed.
