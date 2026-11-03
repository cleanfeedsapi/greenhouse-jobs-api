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

def diff(prev_path, rows):
    """Return (new, closed) ids versus a previous JSON snapshot."""
    try:
        prev = {r["id"] for r in json.load(open(prev_path))}
    except FileNotFoundError:
        prev = set()
    cur = {r["id"] for r in rows}
    return sorted(cur - prev), sorted(prev - cur)

if __name__ == "__main__":
    rows = list(greenhouse_jobs("stripe"))
    print(len(rows), "jobs"); print(rows[0])
