"""AFKBucketを保持するHTTPServer"""

import http.server

from ..domain.afk_bucket import AFKBucket


class WorkHTTPServerSocket(http.server.HTTPServer):
    """AFKBucketを保持するHTTPServer

    http.serverはリクエストごとに新しいHandlerインスタンスを生成するため、
    リクエストをまたいでバケット選択・キャッシュを共有する置き場所として
    サーバーインスタンス自身にAFKBucketを持たせる。
    """

    def __init__(
        self,
        address: tuple[str, int],
        handler_cls: type[http.server.BaseHTTPRequestHandler],
        bucket: AFKBucket,
    ) -> None:
        super().__init__(address, handler_cls)
        self.bucket: AFKBucket = bucket
