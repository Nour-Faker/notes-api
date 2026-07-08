def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert "password" not in data  # never expose password

def test_register_duplicate_email(client):
    # First registration - must actually be sent
    client.post("/api/v1/auth/register", json={
        "email": "same@test.com", "username": "user1", "password": "pass123"
    })
    # Second registration with same email - should fail
    response = client.post("/api/v1/auth/register", json={
        "email": "same@test.com", "username": "user2", "password": "pass123"
    })
    assert response.status_code == 400

def test_login_success(client, registered_user):
    response = client.post("/api/v1/auth/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, registered_user):
    response = client.post("/api/v1/auth/login", data={
        "username": registered_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
def test_pagination(client, auth_headers):
    # Create 3 notes
    for i in range(3):
        client.post("/api/v1/notes/", json={
            "title": f"Note {i}", "content": f"Content {i}"
        }, headers=auth_headers)

    # Get first 2
    response = client.get("/api/v1/notes/?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Get last 1
    response = client.get("/api/v1/notes/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_search(client, auth_headers):
    client.post("/api/v1/notes/", json={
        "title": "FastAPI guide", "content": "How to build APIs"
    }, headers=auth_headers)
    client.post("/api/v1/notes/", json={
        "title": "Docker tutorial", "content": "Containerization basics"
    }, headers=auth_headers)

    # Search by title
    response = client.get("/api/v1/notes/?search=FastAPI", headers=auth_headers)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "FastAPI guide"

    # Search by content
    response = client.get("/api/v1/notes/?search=Containerization", headers=auth_headers)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Docker tutorial"

    # Search with no match
    response = client.get("/api/v1/notes/?search=kubernetes", headers=auth_headers)
    assert len(response.json()) == 0