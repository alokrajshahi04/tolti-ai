def test_room_shell(client):
    r = client.get("/api/v1/rooms/room-1/shell")
    assert r.status_code == 404
