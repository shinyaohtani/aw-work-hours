import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

_SCRIPT_PATH: str = str(Path(__file__).parent.parent / "aw-work-hours")


@pytest.fixture(scope="session")
def aw_module():  # type: ignore[no-untyped-def]
    """aw-work-hours をPythonモジュールとしてimport"""
    loader = importlib.machinery.SourceFileLoader("aw_work_hours", _SCRIPT_PATH)
    spec = importlib.util.spec_from_file_location(
        "aw_work_hours", _SCRIPT_PATH, loader=loader
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _reset_bucket_state(aw_module):  # type: ignore[no-untyped-def]
    """AFKBucket のクラス変数をテスト間でリセット"""
    aw_module.AFKBucket._cached_id = None
    aw_module.AFKBucket._preference = None
    aw_module.WorkRule.MIN_EVENT_SECONDS = 150
    yield
    aw_module.AFKBucket._cached_id = None
    aw_module.AFKBucket._preference = None
    aw_module.WorkRule.MIN_EVENT_SECONDS = 150
