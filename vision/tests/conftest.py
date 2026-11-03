import pytest

from fakes.db import FakeDB
from fakes.blob_storage import FakeBlobStorage

@pytest.fixture
def fake_db(tmp_path):
    db_url = tmp_path / "test.db"
    
    return FakeDB(
        url=f"sqlite:///{db_url}"
    )

@pytest.fixture
def fake_blob_storage():
    return FakeBlobStorage()
