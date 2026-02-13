import pytest

from aw_work_hours.domain.afk_bucket import AFKBucket
from aw_work_hours.domain.work_rule import WorkRule


@pytest.fixture(autouse=True)
def _reset_bucket_state():
    """AFKBucket のクラス変数をテスト間でリセット"""
    AFKBucket.clear_cache()
    AFKBucket.set_preference(None)
    WorkRule.MIN_EVENT_SECONDS = 150
    yield
    AFKBucket.clear_cache()
    AFKBucket.set_preference(None)
    WorkRule.MIN_EVENT_SECONDS = 150
