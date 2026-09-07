def test_room_shell(client):
    r = client.get("/api/v1/rooms/room-1/shell")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "room-1"
    assert data["status"] == "ok"
    assert "name" in data
