"""
Simple endpoint checker for the backend API.

Usage:
  python backend\tools\endpoint_checker.py --base http://localhost:8000/api/v1

It will attempt OPTIONS and the primary method for each endpoint and print a short report.
"""
import argparse
import json
import sys
from urllib.parse import urljoin

try:
    import requests
except Exception:
    requests = None

ENDPOINTS = [
    {"path": "/career/goals", "method": "POST"},
    {"path": "/career/goals", "method": "GET"},
    {"path": "/auth/login", "method": "POST"},
    {"path": "/auth/register", "method": "POST"},
    {"path": "/health", "method": "GET"},
]


def check_with_requests(url, method):
    try:
        if method == "OPTIONS":
            r = requests.options(url, timeout=5)
        elif method == "GET":
            r = requests.get(url, timeout=5)
        elif method == "POST":
            # send minimal JSON to avoid errors
            r = requests.post(url, json={}, timeout=5)
        else:
            r = requests.request(method, url, timeout=5)
        return r.status_code, r.text[:1000]
    except Exception as e:
        return None, str(e)


def check_with_urllib(url, method):
    import urllib.request
    import urllib.error
    from urllib.request import Request

    data = None
    headers = {"Content-Type": "application/json"}
    if method == "POST":
        data = b"{}"

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read(1024).decode(errors="replace")
            return resp.getcode(), body
    except urllib.error.HTTPError as he:
        return he.code, str(he)
    except Exception as e:
        return None, str(e)


def check_endpoint(base, path, method):
    url = base.rstrip("/") + "/" + path.lstrip("/")
    # first OPTIONS
    for m in ["OPTIONS", method]:
        if requests:
            code, body = check_with_requests(url, m)
        else:
            code, body = check_with_urllib(url, m)
        yield m, url, code, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8000/api/v1", help="Base API URL")
    args = parser.parse_args()

    base = args.base
    print("Checking endpoints against:", base)
    results = []
    for ep in ENDPOINTS:
        for method, url, code, body in check_endpoint(base, ep["path"], ep["method"]):
            ok = code is not None and (200 <= code < 400)
            results.append({"path": ep["path"], "method": method, "url": url, "status": code, "ok": ok})
            status_text = f"{code}" if code is not None else "ERROR"
            print(f"{method:7} {url} -> {status_text} {'OK' if ok else 'FAIL'}")

    # summary
    fails = [r for r in results if not r["ok"]]
    print("\nSummary:")
    if not fails:
        print("All endpoints responded with 2xx/3xx status codes (based on minimal checks).")
    else:
        print(f"{len(fails)} endpoints failing or returning non-2xx: ")
        for f in fails:
            print(json.dumps(f))


if __name__ == "__main__":
    main()
