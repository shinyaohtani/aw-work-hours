import sys
from pathlib import Path

import pytest

# パッケージを import 可能にする
sys.path.insert(0, str(Path(__file__).parent.parent))

from aw_work_hours.domain import AFKBucket, WorkRule


@pytest.fixture(autouse=True)
def _reset_bucket_state():
    """AFKBucket のクラス変数をテスト間でリセット"""
    AFKBucket._cached_id = None
    AFKBucket._preference = None
    WorkRule.MIN_EVENT_SECONDS = 150
    yield
    AFKBucket._cached_id = None
    AFKBucket._preference = None
    WorkRule.MIN_EVENT_SECONDS = 150
