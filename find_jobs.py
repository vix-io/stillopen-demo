#!/usr/bin/env python3
"""AI remote job finder, powered by StillOpen.

Search remote jobs, re-check that each one is still open against the
employer's own applicant tracking system (ATS), and print the evidence.
Standard library only, no API key.

    python find_jobs.py "python developer" --loc de --level senior
    python find_jobs.py --verify https://job-boards.greenhouse.io/acme/jobs/123

Data provided by StillOpen (https://stillopen.work). Terms:
https://stillopen.work/api-terms
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://stillopen.work/api/v1"
UA = "stillopen-demo/1.0"

# What each evidence type means, in plain words. Only the first two are
# checks of the posting itself; see https://stillopen.work/llms.txt
EVIDENCE = {
    "ats_verified": "re-checked against the employer's ATS",
    "board_verified": "re-checked by fetching the listing page",
    "employer_board": "on the employer's board when last read",
    "employer_attested": "the employer confirmed it",
    "age_inferred": "no current check",
    "ats_checked_once": "checked once, live, on the employer's ATS",
}


def call(path: str, params: dict | None = None, body: dict | None = None) -> dict:
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": UA, "Accept": "application/json",
        **({"Content-Type": "application/json"} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.exit(f"Rate limited; retry after {e.headers.get('Retry-After', '?')}s.")
        sys.exit(f"StillOpen answered {e.code}: {e.read().decode()[:300]}")


def search(args) -> list[dict]:
    """Search, then re-ask the status of every hit in one batch call."""
    found = call("/jobs", {"q": args.query, "loc": args.loc, "level": args.level,
                           "area": args.area, "limit": args.limit})
    jobs = found["jobs"]
    if not jobs:
        return []
    # The status call is how you re-check ids you already hold (a saved list,
    # a tracker). Shown here right after search; one call carries many ids.
    status = call("/jobs/status", body={"ids": [j["id"] for j in jobs]})
    current = {s["id"]: s for s in status["jobs"]}
    print(f"{found['total']:,} matches; showing {len(jobs)}.\n")
    return [{**j, **current.get(j["id"], {})} for j in jobs]


def show(job: dict) -> None:
    ev = job.get("evidence_type")
    when = (job.get("verified_at") or job.get("last_seen_at") or "")[:16].replace("T", " ")
    places = ", ".join(job.get("locations") or []) or "location not stated"
    print(f"{job.get('title')} — {job.get('company')}")
    print(f"  {places}")
    if job.get("status") == "open":
        print(f"  still open: {EVIDENCE.get(ev, ev or 'no evidence')}, {when} UTC")
    else:
        print(f"  {job.get('status')}: {job.get('closure') or ''} {job.get('closed_at') or ''}")
    if job.get("posting_class") == "evergreen":
        print("  talent pool, not a dated vacancy")
    print(f"  {job.get('canonical_url')}\n")


def verify(url: str) -> None:
    """Ask about any job URL (20 a day free)."""
    r = call("/jobs/verify", {"url": url})
    print(json.dumps({k: v for k, v in r.items() if k != "attribution"}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("query", nargs="?", default="", help="free text, e.g. 'react'")
    p.add_argument("--loc", help="country code (de), region (emea) or 'worldwide'")
    p.add_argument("--level", help="junior, mid, senior, lead, manager, head")
    p.add_argument("--area", help="engineering, product, design, sales_marketing, ...")
    p.add_argument("--limit", type=int, default=10, help="1-20")
    p.add_argument("--verify", metavar="URL", help="check one job URL instead")
    args = p.parse_args()

    if args.verify:
        verify(args.verify)
    else:
        for job in search(args):
            show(job)
    # Required by the API terms wherever StillOpen data is shown.
    print("Data provided by StillOpen — https://stillopen.work")


if __name__ == "__main__":
    main()
