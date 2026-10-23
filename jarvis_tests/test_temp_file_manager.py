from pathlib import Path

import pytest
from services.temp_files import TempFileManager


@pytest.fixture
def manager():
    m = TempFileManager()
    yield m
    m.cleanup()


def test_create_writes_data_and_uses_suffix(manager):
    path = manager.create(b"hello", suffix=".wav")
    assert path.exists()
    assert path.suffix == ".wav"
    assert path.read_bytes() == b"hello"


def test_remove_deletes_file(manager):
    path = manager.create(b"x")
    manager.remove(path)
    assert not path.exists()


def test_remove_twice_does_not_raise(manager):
    path = manager.create(b"x")
    manager.remove(path)
    manager.remove(path)


def test_temp_file_context_removes_file_on_normal_exit(manager):
    with manager.temp_file(b"x", suffix=".png") as path:
        assert path.exists()
    assert not path.exists()


def test_temp_file_context_removes_file_on_exception(manager):
    captured: list[Path] = []
    with pytest.raises(RuntimeError), manager.temp_file(b"x") as path:
        captured.append(path)
        raise RuntimeError("boom")
    assert not captured[0].exists()


def test_cleanup_removes_all_created_files(manager):
    paths = [manager.create(b"a"), manager.create(b"b")]
    manager.cleanup()
    assert all(not p.exists() for p in paths)


def test_cleanup_is_idempotent(manager):
    manager.create(b"a")
    manager.cleanup()
    manager.cleanup()


def test_manager_as_context_cleans_up_on_exit():
    with TempFileManager() as m:
        path = m.create(b"a")
        assert path.exists()
    assert not path.exists()


def test_cleanup_does_not_touch_foreign_files(manager, tmp_path):
    foreign = tmp_path / "keep.txt"
    foreign.write_text("keep")
    manager.create(b"a")
    manager.cleanup()
    assert foreign.exists()
