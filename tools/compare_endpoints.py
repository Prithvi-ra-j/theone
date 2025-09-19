#!/usr/bin/env python3
"""Compare frontend-declared endpoints with backend OpenAPI paths.

Usage: python tools/compare_endpoints.py [--base http://localhost:8000]

The script reads `frontend/src/api/config.js`, extracts string paths under
API_ENDPOINTS, fetches `BASE/api/v1/openapi.json`, and reports endpoints
that the frontend expects but the backend OpenAPI does not expose.
"""
import re
import json
import sys
from urllib.parse import urljoin

try:
    import requests
except Exception:
    print("requests is required. Install with: pip install requests")
    sys.exit(2)

BASE = "http://localhost:8000"
if len(sys.argv) > 1 and sys.argv[1].startswith("--base="):
    BASE = sys.argv[1].split("=", 1)[1]
elif len(sys.argv) > 1:
    BASE = sys.argv[1]

FRONTEND_CONFIG = "frontend/src/api/config.js"


def extract_frontend_paths(js_text: str):
    # Narrow to API_ENDPOINTS block
    m = re.search(r"export\s+const\s+API_ENDPOINTS\s*=\s*\{([\s\S]*?)\};", js_text)
    block = m.group(1) if m else js_text
    # Find all strings that look like '/something' (start with slash)
    paths = set(re.findall(r"['\"](/[^'\"]+)['\"]", block))
    # Remove duplicates and normalize (no trailing slash)
    normalized = set(p.rstrip('/') if p != '/' else p for p in paths)
    return sorted(normalized)


def fetch_openapi(base: str):
    url = urljoin(base.rstrip('/') + '/', 'api/v1/openapi.json')
    print(f"Fetching OpenAPI from: {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    try:
        with open(FRONTEND_CONFIG, 'r', encoding='utf-8') as f:
            js = f.read()
    except FileNotFoundError:
        print(f"Frontend config not found at {FRONTEND_CONFIG}")
        sys.exit(1)

    fe_paths = extract_frontend_paths(js)
    try:
        openapi = fetch_openapi(BASE)
        api_paths = set(openapi.get('paths', {}).keys())
    except Exception as e:
        print(f"Failed to fetch OpenAPI: {e}")
        api_paths = set()

    # Prep comparisons: backend paths include /api/v1 prefix
    missing = []
    present = []
    for p in fe_paths:
        full = '/api/v1' + (p if p.startswith('/') else '/' + p)
        if full in api_paths:
            present.append((p, full))
        else:
            missing.append((p, full))

    print('\nFrontend endpoints found: {}'.format(len(fe_paths)))
    print('Backend (OpenAPI) paths: {}'.format(len(api_paths)))
    print('\nSummary:')
    print('  Present: {}'.format(len(present)))
    print('  Missing: {}'.format(len(missing)))

    if missing:
        print('\nMissing endpoints (frontend -> expected backend path):')
        for orig, full in missing:
            print(f"  {orig}  ->  {full}")
    else:
        print('\nAll frontend endpoints appear in backend OpenAPI (prefix /api/v1).')

    # Optionally write a small JSON report
    report = {
        'frontend_count': len(fe_paths),
        'backend_count': len(api_paths),
        'present': [p for p, _ in present],
        'missing': [p for p, _ in missing],
    }
    with open('tools/endpoint_compare_report.json', 'w', encoding='utf-8') as out:
        json.dump(report, out, indent=2)
    print('\nWrote tools/endpoint_compare_report.json')


if __name__ == '__main__':
    main()
