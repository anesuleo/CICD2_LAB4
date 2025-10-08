import pytest

def user_payload(uid=1, name="Paul", email="pl@atu.ie", age=25, sid="S1234567"):
 return {"user_id": uid, "name": name, "email": email, "age": age, "student_id": sid}

#Test user creating
def test_create_user_ok(client):
    r = client.post("/api/users", json=user_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == 1
    assert data["name"] == "Paul"

#Test for duplicate objects
def test_duplicate_user_id_conflict(client):
    client.post("/api/users", json=user_payload(uid=2))
    r = client.post("/api/users", json=user_payload(uid=2))
    assert r.status_code == 409 # duplicate id -> conflict
    assert "exists" in r.json()["detail"].lower()

#Testing student ID
@pytest.mark.parametrize("bad_sid", ["BAD123", "s1234567", "S123", "S12345678"])
def test_bad_student_id_422(client, bad_sid):
    r = client.post("/api/users", json=user_payload(uid=3, sid=bad_sid))
    assert r.status_code == 422 # pydantic validation error

#Testing user returns 
def test_get_user_404(client):
    r = client.get("/api/users/999")
    assert r.status_code == 404

def test_delete_then_404(client):
    r1 = client.delete("/api/users/1")
    assert r1.status_code == 204
    r2 = client.delete("/api/users/1")
    assert r2.status_code == 404

#Test update user
def test_update_user_ok(client):
    client.post("/api/users", json=user_payload(uid=4))
    r = client.put("/api/users/4", json=user_payload(uid=4, name="Anesu"))
    assert r.status_code == 202
    data = r.json()
    assert data["name"] == "Anesu" 

#Test for bad email
@pytest.mark.parametrize("bad_email", ["lleoo, anesu.com, @leo.com"])
def test_bad_email_422(client, bad_email):
    r = client.post("/api/users", json=user_payload(uid=3, email=bad_email))
    assert r.status_code == 422