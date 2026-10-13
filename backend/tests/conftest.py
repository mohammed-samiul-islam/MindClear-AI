import os
import sys
import tempfile
from pathlib import Path

# Configure env BEFORE the app (and its settings/engine) are imported.
_db = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"
os.environ["LLM_PROVIDER"] = "none"
os.environ.pop("GROQ_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session_a():
    return {"X-Session-ID": "session-aaaaaaaaaaaaaaaa"}


@pytest.fixture
def session_b():
    return {"X-Session-ID": "session-bbbbbbbbbbbbbbbb"}
