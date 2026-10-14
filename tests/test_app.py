import io


def register(client, email="demo@example.com"):
    return client.post(
        "/auth/register",
        data={
            "email": email,
            "password": "correct-horse-battery",
            "confirm_password": "correct-horse-battery",
        },
        follow_redirects=True,
    )


def test_health_endpoint(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_user_can_upload_download_and_delete_a_file(client):
    response = register(client)
    assert response.status_code == 200
    assert b"My files" in response.data

    response = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"hello from cloudbox"), "hello.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"hello.txt" in response.data

    response = client.get("/files/1/download")
    assert response.status_code == 200
    assert response.data == b"hello from cloudbox"
    assert response.headers["Content-Disposition"].startswith("attachment")

    response = client.post("/files/1/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"No files yet" in response.data


def test_disallowed_file_type_is_rejected(client):
    register(client)
    response = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"not executable"), "script.exe")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"file type is not allowed" in response.data
    assert b"No files yet" in response.data


def test_private_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
