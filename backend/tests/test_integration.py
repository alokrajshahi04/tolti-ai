

def test_create_session_and_room(client):
    r = client.post("/api/v1/sessions", json={"display_name": "Alice"})
    assert r.status_code == 201
    session = r.json()
    token = session["session_token"]
    headers = {"Cookie": f"tolti_session={token}"}
    r = client.post("/api/v1/rooms", json={"name": "Room A"}, headers=headers)
    assert r.status_code == 201
    room = r.json()
    assert room["name"] == "Room A"
    assert room["driver_principal_id"] == room["host_principal_id"]


def test_join_via_invite_defaults_to_watcher(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    room = client.post("/api/v1/rooms", json={"name": "Room B"}, headers=host_headers).json()
    invite = client.post(f"/api/v1/rooms/{room['id']}/invites", headers=host_headers).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    r = client.post(
        "/api/v1/rooms/join",
        json={"invite_token": invite["token"]},
        headers=guest_headers,
    )
    assert r.status_code == 200
    assert r.json()["role"] == "watcher"


def test_cross_room_access_forbidden(client):
    host_a = client.post("/api/v1/sessions", json={"display_name": "HostA"}).json()
    token_a = host_a["session_token"]
    headers_a = {"Cookie": f"tolti_session={token_a}"}
    room_a = client.post("/api/v1/rooms", json={"name": "Room A"}, headers=headers_a).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    r = client.get(f"/api/v1/rooms/{room_a['id']}/snapshot", headers=guest_headers)
    assert r.status_code == 404


def test_watcher_cannot_grant_roles(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    room = client.post("/api/v1/rooms", json={"name": "Room C"}, headers=host_headers).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    invite = client.post(f"/api/v1/rooms/{room['id']}/invites", headers=host_headers).json()
    client.post("/api/v1/rooms/join", json={"invite_token": invite["token"]}, headers=guest_headers)
    members = client.get(
        f"/api/v1/rooms/{room['id']}/snapshot",
        headers=host_headers,
    ).json()["memberships"]
    watcher_id = next(m["principal_id"] for m in members if m["role"] == "watcher")
    r = client.post(
        f"/api/v1/rooms/{room['id']}/memberships/{watcher_id}/role",
        json={"role": "reviewer", "expected_room_revision": room["revision"]},
        headers=guest_headers,
    )
    assert r.status_code == 403


def test_host_can_grant_role_and_enforce_single_driver(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    room = client.post("/api/v1/rooms", json={"name": "Room D"}, headers=host_headers).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    invite = client.post(f"/api/v1/rooms/{room['id']}/invites", headers=host_headers).json()
    join = client.post(
        "/api/v1/rooms/join",
        json={"invite_token": invite["token"]},
        headers=guest_headers,
    ).json()
    guest_id = join["principal_id"]
    r = client.post(
        f"/api/v1/rooms/{room['id']}/memberships/{guest_id}/role",
        json={"role": "reviewer", "expected_room_revision": room["revision"]},
        headers=host_headers,
    )
    assert r.status_code == 200
    assert r.json()["role"] == "reviewer"
    members = client.get(
        f"/api/v1/rooms/{room['id']}/snapshot",
        headers=host_headers,
    ).json()["memberships"]
    drivers = [m for m in members if m["role"] == "driver"]
    assert len(drivers) == 1


def test_invalid_invite_rejected(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    client.post("/api/v1/rooms", json={"name": "Room E"}, headers=host_headers).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    r = client.post("/api/v1/rooms/join", json={"invite_token": "bad-token"}, headers=guest_headers)
    assert r.status_code == 404


def test_duplicate_invite_consumption(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    room = client.post("/api/v1/rooms", json={"name": "Room F"}, headers=host_headers).json()
    invite = client.post(f"/api/v1/rooms/{room['id']}/invites", headers=host_headers).json()
    guest1 = client.post("/api/v1/sessions", json={"display_name": "Guest1"}).json()
    guest1_headers = {"Cookie": f"tolti_session={guest1['session_token']}"}
    client.post(
        "/api/v1/rooms/join",
        json={"invite_token": invite["token"]},
        headers=guest1_headers,
    )
    guest2 = client.post("/api/v1/sessions", json={"display_name": "Guest2"}).json()
    guest2_headers = {"Cookie": f"tolti_session={guest2['session_token']}"}
    r = client.post(
        "/api/v1/rooms/join",
        json={"invite_token": invite["token"]},
        headers=guest2_headers,
    )
    assert r.status_code == 404


def test_event_ordering_and_reconnect(client):
    host = client.post("/api/v1/sessions", json={"display_name": "Host"}).json()
    host_token = host["session_token"]
    host_headers = {"Cookie": f"tolti_session={host_token}"}
    room = client.post("/api/v1/rooms", json={"name": "Room G"}, headers=host_headers).json()
    guest = client.post("/api/v1/sessions", json={"display_name": "Guest"}).json()
    guest_token = guest["session_token"]
    guest_headers = {"Cookie": f"tolti_session={guest_token}"}
    invite = client.post(f"/api/v1/rooms/{room['id']}/invites", headers=host_headers).json()
    client.post("/api/v1/rooms/join", json={"invite_token": invite["token"]}, headers=guest_headers)
    events1 = client.get(
        f"/api/v1/rooms/{room['id']}/events?after_seq=0",
        headers=host_headers,
    ).json()
    assert len(events1["items"]) >= 2
    seqs = [e["seq"] for e in events1["items"] if e["seq"] is not None]
    assert seqs == sorted(seqs)
    last_seq = events1["next_after_seq"]
    events2 = client.get(
        f"/api/v1/rooms/{room['id']}/events?after_seq={last_seq}",
        headers=guest_headers,
    ).json()
    assert events2["items"] == []


def test_session_revocation(client):
    session = client.post("/api/v1/sessions", json={"display_name": "Revoker"}).json()
    token = session["session_token"]
    csrf = session["csrf_token"]
    headers = {"Cookie": f"tolti_session={token}"}
    r = client.delete("/api/v1/sessions/current", headers=headers, params={"csrf_token": csrf})
    assert r.status_code in (204, 405)
    r2 = client.get("/api/v1/sessions/current", headers=headers)
    assert r2.status_code == 401
