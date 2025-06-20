import os
import pytest

from app.services.system_service import SystemService
from app.core import config

@pytest.mark.asyncio
async def test_cleanup_temp_files(monkeypatch, tmp_path):
    monkeypatch.setattr(config.settings, "TEMP_DIR", str(tmp_path))
    # create temporary files
    file1 = tmp_path / "a.txt"
    file1.write_bytes(b"12345")
    file2 = tmp_path / "b.txt"
    file2.write_bytes(b"hi")

    service = SystemService()
    result = await service.cleanup_temp_files()
    assert result["cleaned"] == 2
    assert result["size_freed"] >= 7
    assert not file1.exists() and not file2.exists()
