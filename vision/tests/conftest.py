import pytest

from fakes.db import FakeDB

@pytest.fixture
def fake_db(tmp_path):
    db_url = tmp_path / "test.db"
    
    return FakeDB(
        url=f"sqlite:///{db_url}"
    )
