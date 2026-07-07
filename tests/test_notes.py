def test_create_note(client, auth_headers):
    response = client.post("/api/v1/notes/", json={
        "title": "Test note",
        "content": "Hello world",
        "tag": "work"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test note"
    assert data["tag"] == "work"

def test_get_notes_empty(client, auth_headers):
    response = client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_notes_returns_only_own(client):
    # Create two users
    client.post("/api/v1/auth/register", json={
        "email": "a@test.com", "username": "usera", "password": "pass123"
    })
    client.post("/api/v1/auth/register", json={
        "email": "b@test.com", "username": "userb", "password": "pass123"
    })

    def login(username):
        r = client.post("/api/v1/auth/login", data={"username": username, "password": "pass123"})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    headers_a = login("usera")
    headers_b = login("userb")

    client.post("/api/v1/notes/", json={"title": "A note", "content": "A"}, headers=headers_a)
    client.post("/api/v1/notes/", json={"title": "B note", "content": "B"}, headers=headers_b)

    notes_a = client.get("/api/v1/notes/", headers=headers_a).json()
    notes_b = client.get("/api/v1/notes/", headers=headers_b).json()

    assert len(notes_a) == 1
    assert notes_a[0]["title"] == "A note"
    assert len(notes_b) == 1
    assert notes_b[0]["title"] == "B note"

def test_delete_note(client, auth_headers):
    note = client.post("/api/v1/notes/", json={
        "title": "To delete", "content": "bye"
    }, headers=auth_headers).json()

    response = client.delete(f"/api/v1/notes/{note['id']}", headers=auth_headers)
    assert response.status_code == 204

def test_cannot_access_without_token(client):
    response = client.get("/api/v1/notes/")
    assert response.status_code == 401