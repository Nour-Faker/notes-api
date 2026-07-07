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