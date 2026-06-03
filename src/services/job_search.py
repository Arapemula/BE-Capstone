import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request


JOBICY_API_URL = "https://jobicy.com/api/v2/remote-jobs"


def get_job_search_timeout():
    try:
        return float(os.getenv("JOB_SEARCH_TIMEOUT_SECONDS", "8"))
    except ValueError:
        return 8.0


def clamp_limit(value, default=6):
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default

    return max(1, min(12, number))


def normalize_role_query(role):
    query = str(role or "").strip()
    query = re.sub(r"\b(junior|senior|lead|staff|associate|entry level|entry-level)\b", "", query, flags=re.I)
    query = re.sub(r"\s+", " ", query).strip()
    return query or "developer"


def normalize_jobicy_geo(location):
    value = str(location or "").strip().lower()
    if not value:
        return ""

    if value in {"indonesia", "jakarta", "bandung", "surabaya", "yogyakarta", "jogja"}:
        return "apac"

    allowed_values = {
        "apac", "emea", "latam", "usa", "canada", "uk", "europe", "australia",
        "singapore", "philippines", "vietnam", "thailand", "japan", "south-korea",
    }
    return value if value in allowed_values else ""


def strip_html(value):
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_salary(job):
    salary_min = job.get("salaryMin")
    salary_max = job.get("salaryMax")
    currency = job.get("salaryCurrency") or ""
    period = job.get("salaryPeriod") or ""

    if not salary_min and not salary_max:
        return ""

    if salary_min and salary_max:
        amount = f"{salary_min} - {salary_max}"
    else:
        amount = str(salary_min or salary_max)

    return " ".join(part for part in [currency, amount, period] if part)


def normalize_jobicy_job(job):
    return {
        "id": str(job.get("id") or job.get("url") or ""),
        "title": job.get("jobTitle") or "Lowongan relevan",
        "company": job.get("companyName") or "Perusahaan tidak tersedia",
        "location": job.get("jobGeo") or "Remote",
        "type": job.get("jobType") or "",
        "level": job.get("jobLevel") or "",
        "excerpt": strip_html(job.get("jobExcerpt") or job.get("jobDescription"))[:220],
        "salary": format_salary(job),
        "url": job.get("url") or "",
        "source": "Jobicy",
        "postedAt": job.get("pubDate") or "",
    }


def fetch_job_vacancies(role, location="", limit=6):
    query = normalize_role_query(role)
    count = clamp_limit(limit)
    params = {
        "count": count,
        "tag": query,
    }
    geo = normalize_jobicy_geo(location)
    if geo:
        params["geo"] = geo

    url = f"{JOBICY_API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SkillMap/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=get_job_search_timeout()) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
        raise RuntimeError("Info loker belum bisa dimuat dari provider eksternal.") from exc

    raw_jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    jobs = [
        normalize_jobicy_job(job)
        for job in raw_jobs
        if isinstance(job, dict)
    ][:count]

    return {
        "provider": "jobicy",
        "query": query,
        "location": geo or "remote-anywhere",
        "jobs": jobs,
    }
