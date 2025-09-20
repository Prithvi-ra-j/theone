import requests

# Target career goals endpoint (match running server port)
u = 'http://localhost:8000/api/v1/career/goals'

print('\n--- OPTIONS (simulated browser preflight)')
headers = {
    'Origin': 'http://localhost:5173',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'authorization,content-type',
}
try:
    r = requests.options(u, headers=headers, timeout=5)
    print(r.status_code, r.headers)
    print('body:', r.text)
except Exception as e:
    print('OPTIONS error', e)

print('\n--- POST (no auth, sample payload)')
payload = {'title': 'Test Goal', 'description': 'desc', 'target_date': '2025-12-31'}
try:
    r = requests.post(u, json=payload, timeout=5)
    print(r.status_code, r.text)
except Exception as e:
    print('POST error', e)
