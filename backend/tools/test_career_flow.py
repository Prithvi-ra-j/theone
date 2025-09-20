# Use the running backend port (8000); previous runs used 8001 intermittently which caused connection refused errors
import requests
BASE = 'http://127.0.0.1:8000/api/v1'
# Register
print('Registering...')
r = requests.post(BASE+'/auth/register', json={'email':'devtest@example.com','password':'password123','name':'Dev Test'})
print('reg', r.status_code, r.text)
# Login
print('Logging in...')
r = requests.post(BASE+'/auth/login', json={'email':'devtest@example.com','password':'password123'})
print('login', r.status_code, r.text)
if r.status_code==200:
    token=r.json().get('access_token')
    headers={'Authorization':f'Bearer {token}'}
    print('Creating career goal...')
    payload={'title':'Test Goal from script','description':'Testing API','target_date':'2025-12-31'}
    rc = requests.post(BASE+'/career/goals', json=payload, headers=headers)
    print('create goal', rc.status_code, rc.text)
else:
    print('login failed; cannot create goal')
