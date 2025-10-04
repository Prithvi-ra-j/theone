import json

def test_e2e_happy_path(client, auth_headers):
    # Create a goal (career)
    goal_payload = {
        "title": "Get a backend internship",
        "description": "Practice FastAPI and SQLAlchemy",
    }
    r = client.post('/api/v1/career/goals', json=goal_payload, headers=auth_headers)
    assert r.status_code in (200, 201)
    goal = r.get_json()
    assert goal.get('id')

    # Ask AI (conversation)
    conv = client.post('/api/v1/ai/conversation', json={"message": "How should I prepare this month?"}, headers=auth_headers)
    assert conv.status_code == 200
    conv_data = conv.get_json()
    assert conv_data.get('reply')

    # Start learning path
    lp = client.get('/api/v1/career/learning-paths', headers=auth_headers)
    assert lp.status_code == 200
    paths = lp.get_json()
    if paths:
        pid = paths[0].get('id')
        start = client.put(f'/api/v1/career/learning-paths/{pid}', json={"started_at": "2025-10-02T00:00:00Z"}, headers=auth_headers)
        assert start.status_code in (200, 204)
