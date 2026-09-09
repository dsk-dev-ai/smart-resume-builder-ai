import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    return app_module.app.test_client()


def test_home_get_renders_form(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_home_post_missing_fields_flashes_error(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module.app, "root_path", str(tmp_path))
    client.post("/", data={"name": "A", "skills": "", "experience": ""})
    with client.session_transaction() as sess:
        flashes = sess.get("_flashes", [])
        assert any("All fields are required" in msg for _, msg in flashes)


def test_home_post_valid_renders_preview(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "generate_resume_text", lambda *a, **k: "RESUME BODY")
    monkeypatch.setattr(
        app_module, "create_pdf", lambda text, filename: str(tmp_path / filename)
    )
    resp = client.post(
        "/",
        data={"name": "Ada", "skills": "Python", "experience": "5 years"},
    )
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "RESUME BODY" in body


def test_download_serves_pdf(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app_module.app, "root_path", str(tmp_path))
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "abc123.pdf").write_bytes(b"%PDF-1.4 test")

    resp = client.get("/download/abc123.pdf")
    assert resp.status_code == 200
    assert resp.data == b"%PDF-1.4 test"


def test_download_missing_file_redirects(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module.app, "root_path", str(tmp_path))
    monkeypatch.setattr(app_module.os.path, "isfile", lambda p: False)
    resp = client.get("/download/nope.pdf")
    assert resp.status_code == 302


def test_wrap_text_splits_long_lines():
    c = _FakeCanvas()
    lines = app_module._wrap_text("word " * 30, 200, c)
    assert len(lines) > 1
    assert all(line.strip() for line in lines)


class _FakeCanvas:
    def stringWidth(self, text, *_args):
        return len(text) * 7