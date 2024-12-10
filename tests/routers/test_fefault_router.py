def test_ping(client):
    response = client.get("/default/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
