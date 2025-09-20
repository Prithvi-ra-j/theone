import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=10)
    print('health', r.status_code, r.text)
except Exception as e:
    print('health error', e)
