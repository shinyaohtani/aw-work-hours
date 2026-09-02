import pytest


@pytest.fixture(autouse=True)
def _reset_bucket_state():
    """互換性維持用のno-opフィクスチャ

    AFKBucket・MIN_EVENT_SECONDSはインスタンス状態になり、
    テスト間で共有されるクラス変数が無くなったためリセット不要。
    """
    yield
