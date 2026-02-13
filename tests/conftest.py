import pytest

from aw_work_hours.domain.afk_bucket import AFKBucket
from aw_work_hours.domain.work_rule import WorkRule


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
