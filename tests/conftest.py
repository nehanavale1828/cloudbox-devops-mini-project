import pytest

from storage_app import create_app
from storage_app.extensions import db


@pytest.fixture()
def app(tmp_path):
    database = tmp_path / "test.db"
    upload_root = tmp_path / "uploads"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database}",
            "STORAGE_BACKEND": "local",
            "STORAGE_ROOT": str(upload_root),
            "MAX_UPLOAD_MB": 2,
            "MAX_CONTENT_LENGTH": 2 * 1024 * 1024,
        }
    )
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
