#!/usr/bin/env python3
"""
Check API endpoints defined in frontend/src/api/config.js

Usage:
  python tools/check_endpoints.py [--base BASE_URL] [--timeout SECONDS] [--fail-on-error]

By default BASE_URL is http://localhost:8000/api/v1

The script will:
- parse API endpoint paths from the API_ENDPOINTS object in config.js
- deduplicate and sort them
- for each endpoint perform a HEAD request; if not allowed or fails, fallback to GET
- print a table of results and a summary

Return code: 0 (by default). Use --fail-on-error to exit with code 2 when any endpoint is not 2xx.
"""
import argparse
import os
import re
import sys
import textwrap
from urllib.parse import urljoin

try:
    import requests
except Exception:
    requests = None


def find_api_endpoints(config_js_path):
    with open(config_js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the export const API_ENDPOINTS = {...} block
    m = re.search(r"export\s+const\s+API_ENDPOINTS\s*=\s*\{", content)
    if not m:
        raise RuntimeError('Could not find API_ENDPOINTS object in config.js')

    start = m.end() - 1
    # find matching closing brace
    level = 0
    end = None
    for i in range(start, len(content)):
        if content[i] == '{':
            level += 1
        elif content[i] == '}':
            level -= 1
            if level == 0:
                end = i
                break
    if end is None:
        raise RuntimeError('Could not parse API_ENDPOINTS block (unmatched braces)')

    block = content[start:end+1]

    # find all string literal paths starting with /
    paths = re.findall(r"(['\"])(/[^'\"]+)\1", block)
    endpoints = sorted({p[1] for p in paths})
    return endpoints


def check_endpoint(url, timeout=5, force_get=False, headers=None):
    # If force_get is True, try GET first
    headers = headers or {}
    try_methods = ['GET'] if force_get else ['HEAD', 'GET']
    last_exc = None
    for method in try_methods:
        try:
            if method == 'HEAD':
                r = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
            else:
                r = requests.get(url, allow_redirects=True, timeout=timeout, headers=headers)
            # If HEAD is explicitly rejected with 405, continue to try GET
            if method == 'HEAD' and r.status_code == 405:
                # try GET next
                last_exc = None
                continue
            return r.status_code, method
        except requests.exceptions.RequestException as e:
            last_exc = e
            # try next method
            continue
    # if we get here, all methods failed
    return (None, str(last_exc))


def make_base_url(base):
    # Normalize base to ensure it ends with /api/v1 when appropriate
    if base.endswith('/'):
        base = base[:-1]
    return base


def main():
    parser = argparse.ArgumentParser(
        description='Check API endpoints found in frontend/src/api/config.js'
    )
    parser.add_argument('--base', '-b', help='API base URL (defaults to http://localhost:8000/api/v1)')
    parser.add_argument('--config', '-c', help='Path to config.js (auto-detected)', default=None)
    parser.add_argument('--timeout', type=float, default=5.0, help='Request timeout seconds')
    parser.add_argument('--fail-on-error', action='store_true', help='Exit non-zero if any endpoint is not 2xx')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--token', '-t', help='Bearer token to use for Authorization header')
    parser.add_argument('--sample-id', default='1', help='Sample id to substitute for parameterized endpoints (default: 1)')
    parser.add_argument('--force-get', action='store_true', help='Always use GET instead of HEAD')
    parser.add_argument('--skip-parameterized', action='store_true', help='Skip endpoints that contain parameter placeholders')
    args = parser.parse_args()

    if requests is None:
        print('The `requests` library is required. Please install it: pip install requests')
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    default_config = os.path.join(project_root, 'frontend', 'src', 'api', 'config.js')
    config_path = args.config or default_config

    if not os.path.exists(config_path):
        print(f'config.js not found at {config_path}')
        sys.exit(1)

    try:
        endpoints = find_api_endpoints(config_path)
    except Exception as e:
        print('Error parsing config.js:', e)
        sys.exit(1)

    # Determine base URL
    base = args.base or os.environ.get('API_BASE') or os.environ.get('VITE_API_BASE_URL')
    if not base:
        # default to localhost with api/v1
        base = 'http://localhost:8000/api/v1'
    base = make_base_url(base)
    token = args.token or os.environ.get('API_TOKEN') or os.environ.get('VITE_API_TOKEN')
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    print('\nChecking endpoints against base:', base)
    print('Found', len(endpoints), 'endpoints in API_ENDPOINTS.\n')

    results = []
    param_patterns = [r'\{[^}]+\}', r':\w+', r'<[^>]+>']
    import re as _re
    for ep in endpoints:
        is_param = any(_re.search(p, ep) for p in param_patterns)
        ep_to_check = ep
        note = None
        if is_param:
            if args.skip_parameterized:
                results.append((ep, None, None, 'skipped (parameterized)'))
                continue
            # substitute sample id
            sample = args.sample_id
            ep_to_check = _re.sub(r'\{[^}]+\}', sample, ep)
            ep_to_check = _re.sub(r':(\w+)', sample, ep_to_check)
            ep_to_check = _re.sub(r'<[^>]+>', sample, ep_to_check)
            note = f'substituted sample id={sample}'

        url = base + ep_to_check if ep_to_check.startswith('/') else base + '/' + ep_to_check
        if args.verbose:
            if note:
                print('Checking', url, '(', note, ')')
            else:
                print('Checking', url)
        status, method_or_err = check_endpoint(url, timeout=args.timeout, force_get=args.force_get, headers=headers)
        results.append((ep, url, status, method_or_err))

    # Print formatted results
    ok = []
    auth = []
    not_found = []
    server_err = []
    timeout = []
    other = []

    for ep, url, status, info in results:
        if status is None:
            timeout.append((ep, url, info))
        elif 200 <= status < 300:
            ok.append((ep, url, status, info))
        elif status in (301, 302, 303, 307, 308):
            ok.append((ep, url, status, info))
        elif status in (401, 403):
            auth.append((ep, url, status, info))
        elif status == 404:
            not_found.append((ep, url, status, info))
        elif 500 <= status < 600:
            server_err.append((ep, url, status, info))
        else:
            other.append((ep, url, status, info))

    def short(s):
        return s if len(s) <= 70 else s[:67] + '...'

    print('\nResults:')
    if ok:
        print('\n  OK (2xx/3xx)')
        for ep, url, status, info in ok:
            print(f'   [OK] {status} {short(url)}')

    if auth:
        print('\n  Auth required (401/403)')
        for ep, url, status, info in auth:
            print(f' [AUTH] {status} {short(url)}')

    if not_found:
        print('\n  Not Found (404)')
        for ep, url, status, info in not_found:
            print(f' [404] {short(url)}')

    if server_err:
        print('\n  Server Error (5xx)')
        for ep, url, status, info in server_err:
            print(f' [5xx] {status} {short(url)}')

    if timeout:
        print('\n  Error / Timeout')
        for ep, url, info in timeout:
            print(f' [ERR] {short(url)} -> {info}')

    if other:
        print('\n  Other statuses')
        for ep, url, status, info in other:
            print(f' [??] {status} {short(url)} -> {info}')

    total = len(results)
    print('\nSummary: total=%d  ok=%d  auth=%d  not_found=%d  server_err=%d  timeout=%d  other=%d' % (
        total, len(ok), len(auth), len(not_found), len(server_err), len(timeout), len(other)
    ))

    if args.fail_on_error and (len(not_found) or len(server_err) or len(timeout) or len(other)):
        sys.exit(2)
    print('\nDone.')


if __name__ == '__main__':
    main()
