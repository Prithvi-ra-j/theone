import json

def test_healthz(client):
    resp = client.get('/api/v1/healthz')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'db' in data
    assert 'ai' in data and 'available' in data['ai']
    assert 'faiss' in data and 'index_count' in data['faiss']
    assert 'version' in data and 'uptime_seconds' in data
