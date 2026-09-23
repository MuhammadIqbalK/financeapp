def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_register_login_me(client):
    resp = client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "a@b.com"
    dup = client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert dup.status_code == 409
    bad = client.post("/api/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert bad.status_code == 401
    ok = client.post("/api/auth/login", json={"email": "a@b.com", "password": "secret123"})
    assert ok.status_code == 200


def test_default_categories_seeded(auth_client):
    cats = auth_client.get("/api/categories").json()
    names = {c["name"] for c in cats}
    assert {"Salary", "Food", "Transport", "Bills"} <= names
    assert len(cats) == 13
