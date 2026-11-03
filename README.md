# Greenhouse Jobs API: how to get every job from any Greenhouse job board as JSON

Greenhouse exposes a **public, unauthenticated Job Board API** for every company that uses it for its careers page. No API key, no login. This guide documents the endpoints, the fields you get back, pagination and limits, and ships a dependency-free Python example.

## The endpoint

```
GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}
GET https://boards-api.greenhouse.io/v1/boards/{board_token}/departments
GET https://boards-api.greenhouse.io/v1/boards/{board_token}/offices
```

`board_token` is the slug in the careers URL: `https://boards.greenhouse.io/stripe` → `stripe`; `https://job-boards.greenhouse.io/airbnb` → `airbnb`. Companies that embed the board on their own domain still have a token; view the page source and look for `boards.greenhouse.io/embed/job_board?for=<token>`.

## What you get back

`/jobs` returns `{"jobs": [...], "meta": {"total": N}}`. Each job:

| Field | Example | Notes |
|---|---|---|
| `id` | `4012345678` | stable numeric id, diff it between runs to detect new and closed roles |
| `title` | `Software Engineer, Payments` | |
| `location.name` | `Remote, US` | free text as the company wrote it |
| `absolute_url` | `https://boards.greenhouse.io/stripe/jobs/4012345678` | apply page |
| `updated_at` | `2026-10-21T09:12:00-04:00` | ISO 8601 with offset |
| `first_published` | `2026-10-01T08:00:00-04:00` | present on most boards |
| `departments[]`, `offices[]` | `[{"id":..., "name":"Engineering"}]` | only with `content=true` or on `/jobs/{id}` |
| `content` | HTML string | only with `content=true`; HTML-escaped on the list endpoint |
| `metadata[]` | custom fields | varies per company |

## Pagination and limits

There is **no pagination**: `/jobs` returns the whole board in one response (boards with 1,000+ jobs return several MB). There is no documented rate limit, but the API is served through a CDN; a few requests per second per client is fine, and you should cache. Responses are `Cache-Control: max-age` friendly.

## Python example (stdlib only)

```python
import json, urllib.request

def greenhouse_jobs(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    req = urllib.request.Request(url, headers={"User-Agent": "your-app/1.0 (contact@example.com)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    for j in data["jobs"]:
        yield {
            "id": str(j["id"]),
            "title": j["title"],
            "location": (j.get("location") or {}).get("name"),
            "url": j["absolute_url"],
            "updated_at": j.get("updated_at"),
            "posted_at": j.get("first_published"),
        }

if __name__ == "__main__":
    rows = list(greenhouse_jobs("stripe"))
    print(len(rows), "jobs"); print(rows[0])
```

See `example.py` for the same with a diff against a previous snapshot.

## Finding Greenhouse boards

Search engines: `site:boards.greenhouse.io` or `site:job-boards.greenhouse.io`. Many company careers pages are iframes of the board; the token is in the iframe URL.

## Common questions

**Is there an official Greenhouse Job Board API doc?** Yes, Greenhouse publishes it for board embedding; the list above is what it returns in practice as of late 2026.

**Can I apply through the API?** POST applications need a Job Board API key issued to the company; this repository covers read-only listing.

**Does `content=true` slow things down?** Yes, it adds the full HTML description per job; fetch the list without it and `/jobs/{id}` for the roles you care about.


## Hosted version, pay per result

If you would rather not run and maintain this yourself, the same logic runs as a pay-per-result Apify Actor by CleanFeeds: https://apify.com/cleanfeedsapi/greenhouse-jobs-feed ($1.50 per 1,000 rows, no subscription, JSON/CSV/Excel export, API, scheduling, n8n/Make/Zapier and MCP integrations). A multi-ATS variant that mixes Greenhouse, Lever, Ashby, Workday, SmartRecruiters and Recruitee boards in one run: https://apify.com/cleanfeedsapi/ats-jobs-feed


## Legal note

These are public, unauthenticated endpoints that the career pages themselves load. Job postings are employer announcements and belong to the employers. Be polite: identify your client with a User-Agent, cache results, and do not hammer the endpoints. Nothing here is affiliated with or endorsed by Greenhouse.
