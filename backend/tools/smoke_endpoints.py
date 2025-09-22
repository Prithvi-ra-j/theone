#!/usr/bin/env python3
"""
Smoke test runner for API endpoints declared in frontend/src/api/config.js

Saves a clear report of which endpoints returned 2xx, 4xx, 5xx, or timed out.

Usage:
  python backend/tools/smoke_endpoints.py [--base BASE_URL] [--token TOKEN] [--timeout 5]

This script is conservative: it substitutes sample ids for parameterized paths and
will attempt GET on each endpoint (HEAD isn't widely supported in some APIs).
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import urljoin

try:
    import requests
except Exception:
    print('Please install requests: pip install requests')
    sys.exit(1)


def find_endpoints_from_frontend(config_path):
    if not os.path.exists(config_path):
        return []
    text = open(config_path, 'r', encoding='utf-8').read()
    m = re.search(r"export\s+const\s+API_ENDPOINTS\s*=\s*\{", text)
    if not m:
        return []
    start = m.end() - 1
    level = 0
    end = None
    for i in range(start, len(text)):
        if text[i] == '{':
            level += 1
        elif text[i] == '}':
            level -= 1
            if level == 0:
                end = i
                break
    if end is None:
        return []
    block = text[start:end+1]
    paths = re.findall(r"(['\"])(/[^'\"]+)\1", block)
    return sorted({p[1] for p in paths})


def normalize_base(base):
    if base.endswith('/'):
        return base[:-1]
    return base


def substitute_params(path, sample_id='1'):
    # Replace {id}, :id, <id> with sample
    path = re.sub(r"\{[^}]+\}", sample_id, path)
    path = re.sub(r":(\w+)", sample_id, path)
    path = re.sub(r"<[^>]+>", sample_id, path)
    return path


def check_endpoint(url, headers=None, timeout=10):
    headers = headers or {}
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            return r.status_code, r.text
        except requests.exceptions.RequestException as e:
            if attempt == attempts:
                return None, str(e)
            # simple backoff
            import time
            time.sleep(0.5 * attempt)
            continue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', '-b', help='Base URL (e.g. http://localhost:8000/api/v1)')
    parser.add_argument('--config', '-c', help='Path to frontend config.js', default=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'src', 'api', 'config.js'))
    parser.add_argument('--token', '-t', help='Bearer token')
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--sample-id', default='1')
    args = parser.parse_args()

    endpoints = find_endpoints_from_frontend(args.config)
    if not endpoints:
        print('No endpoints found in frontend config; falling back to a default list')
        # Small default list of important endpoints if config not present
        endpoints = [
            '/auth/demo-login',
            '/career/goals',
            '/career/tasks',
            '/career/feedback',
            '/habits/dashboard',
            '/mood/logs',
            '/mini-assistant',
            '/gamification/leaderboard',
        ]

    base = args.base or os.environ.get('VITE_API_BASE_URL') or 'http://localhost:8000/api/v1'
    base = normalize_base(base)
    headers = {}
    token = args.token
    # If token not provided, try demo login
    if not token:
        demo_login_url = normalize_base(base) + '/auth/demo-login'
        try:
            resp = requests.post(demo_login_url, json={"email": "demo@example.com"}, timeout=10)
            if resp.status_code == 200:
                token = resp.json().get('access_token')
                print('Obtained demo token via /auth/demo-login')
        except Exception:
            # ignore demo login failure; proceed unauthenticated
            pass

    if token:
        headers['Authorization'] = f'Bearer {token}'

    results = []
    print(f'Checking {len(endpoints)} endpoints against base {base}\n')
    for ep in endpoints:
        ep_disp = ep
        ep_sub = substitute_params(ep, args.sample_id)
        # ensure leading slash
        if not ep_sub.startswith('/'):
            ep_sub = '/' + ep_sub
        url = base + ep_sub
        status, body_or_err = check_endpoint(url, headers=headers, timeout=args.timeout)
        # For reporting, truncate long bodies but keep full body in report for failures
        short_info = None
        if status is None:
            print(f'[ERR] {ep_disp} -> {body_or_err}')
            short_info = str(body_or_err)[:200]
        else:
            print(f'[{status}] {ep_disp} -> {url}')
            short_info = (body_or_err[:200] + '...') if len(body_or_err) > 200 else body_or_err
        results.append((ep_disp, url, status, short_info, body_or_err))

    # Summary
    ok = sum(1 for r in results if r[2] and 200 <= r[2] < 300)
    auth = sum(1 for r in results if r[2] in (401, 403))
    notfound = sum(1 for r in results if r[2] == 404)
    server = sum(1 for r in results if r[2] and 500 <= r[2] < 600)
    err = sum(1 for r in results if r[2] is None)

    print('\nSummary:')
    print(f'  total={len(results)} ok={ok} auth={auth} not_found={notfound} server_err={server} errors={err}')

    # Prepare structured report: split into working (2xx) and not_working (others)
    working = []
    not_working = []
    for r in results:
        entry = {'endpoint': r[0], 'url': r[1], 'status': r[2], 'summary': r[3], 'full': r[4]}
        if r[2] and 200 <= r[2] < 300:
            working.append(entry)
        else:
            not_working.append(entry)

    report = {'working': working, 'not_working': not_working, 'summary': {'total': len(results), 'ok': ok, 'auth': auth, 'not_found': notfound, 'server_err': server, 'errors': err}}

    # Write report
    report_path = os.path.join(os.path.dirname(__file__), 'smoke_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f'Report written to {report_path}')

    # Print quick lists
    print('\nWorking endpoints:')
    for e in working:
        print(f"  [{e['status']}] {e['endpoint']} -> {e['url']}")

    print('\nNot working endpoints:')
    for e in not_working:
        st = 'ERR' if e['status'] is None else e['status']
        print(f"  [{st}] {e['endpoint']} -> {e['url']}")

    # Exit non-zero if any server errors or errors
    if server or err:
        sys.exit(2)


if __name__ == '__main__':
    main()
