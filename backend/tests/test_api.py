def _analyze(client, headers, text):
    r = client.post("/analyze", json={"text": text}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["llm_provider"] == "none"


def test_session_header_required(client):
    assert client.get("/tasks").status_code == 400
    assert client.get("/tasks", headers={"X-Session-ID": "short"}).status_code == 400
    assert client.post("/analyze", json={"text": "call mom"}).status_code == 400


def test_analyze_uses_rules_fallback(client, session_a):
    data = _analyze(client, session_a, "pay rent tomorrow, gym on friday")
    assert data["source"] == "rules"
    assert [t["category"] for t in data["tasks"]] == ["Finance", "Health"]
    assert data["tasks"][0]["deadline"] is not None


def test_session_isolation(client, session_a, session_b):
    a = _analyze(client, session_a, "isolation task A")
    b = _analyze(client, session_b, "isolation task B")
    a_task_id = a["tasks"][0]["id"]

    a_tasks = [t["task"] for t in client.get("/tasks", headers=session_a).json()["tasks"]]
    b_tasks = [t["task"] for t in client.get("/tasks", headers=session_b).json()["tasks"]]
    assert "Isolation task A" in a_tasks and "Isolation task B" not in a_tasks
    assert "Isolation task B" in b_tasks and "Isolation task A" not in b_tasks

    a_convs = {c["id"] for c in client.get("/conversions", headers=session_a).json()["conversions"]}
    assert a["conversion_id"] in a_convs and b["conversion_id"] not in a_convs

    # B cannot modify or delete A's task.
    assert client.patch(f"/tasks/{a_task_id}", json={"completed": True}, headers=session_b).status_code == 404
    assert client.delete(f"/tasks/{a_task_id}", headers=session_b).status_code == 404

    # A can.
    r = client.patch(f"/tasks/{a_task_id}", json={"completed": True}, headers=session_a)
    assert r.status_code == 200 and r.json()["completed"] is True
    assert client.delete(f"/tasks/{a_task_id}", headers=session_a).status_code == 204


def test_filters(client):
    h = {"X-Session-ID": "session-filters-0000000"}
    _analyze(client, h, "pay bill, call mom")
    r = client.get("/tasks", params={"category": "Finance"}, headers=h).json()["tasks"]
    assert [t["task"] for t in r] == ["Pay bill"]


def test_empty_input_rejected(client, session_a):
    assert client.post("/analyze", json={"text": ""}, headers=session_a).status_code == 422
    assert client.post("/analyze", json={"text": " ,; "}, headers=session_a).status_code == 422
