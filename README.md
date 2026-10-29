# aw-work-hours

[ActivityWatch](https://activitywatch.net/) から日ごとの勤務時間を取得・可視化するCLIツール。

## 必要条件

- Python 3.9+
- ActivityWatch がローカルで起動していること（`http://127.0.0.1:5600`）

本アプリが参照するActivityWatchのインストールは公式サイトを参照: https://activitywatch.net/downloads/

## インストール

```bash
git clone git@github.com:shinyaohtani/aw-work-hours.git
cd aw-work-hours
chmod +x aw-work-hours
```

PATHの通った場所にシンボリックリンクを作成するか、エイリアスを設定してください。

## 使い方

### 基本

```bash
# 今月の勤務時間をテキスト表示
aw-work-hours

# 先月の勤務時間を表示
aw-work-hours --month=last

# 特定の月を指定
aw-work-hours --month=2025-01

# 全期間を表示
aw-work-hours --month=all
```

### 出力形式

```bash
# CSVファイルに出力
aw-work-hours -o work.csv

# HTML形式でブラウザ表示（タイムラインUI）
aw-work-hours --html

# 時刻をコロンなし（HHMM）で表示
aw-work-hours --no-colon

# 進捗メッセージを非表示
aw-work-hours -q
```

### 出力例（テキスト）

```
2025-01-06 月   09:15 - 18:30   (9.3h)   -1.2h (max:-0.5h)
2025-01-07 火   08:45 - 19:00   (10.3h)  -0.8h (max:-0.3h)
2025-01-08 水   09:00 - 17:45   (8.8h)
2025-01-11 土*  10:00 - 14:00   (4.0h)
```

- `*` は土日祝日に勤務があった日
- `-1.2h` はAFK（離席）時間
- `max:-0.5h` は最大の連続離席時間

## オプション一覧

| オプション | 短縮形 | 説明 |
|-----------|-------|------|
| `--month=MONTH` | `-m` | 対象月: `this`(今月), `last`(先月), `all`(全期間), `YYYY-MM` |
| `--output=FILE` | `-o` | CSV出力ファイル名 |
| `--html` | | HTML形式でブラウザ表示 |
| `--no-colon` | | 時刻をHHMM形式で出力 |
| `--quiet` | `-q` | 進捗メッセージを非表示 |
| `--bucket=NAME` | `-b` | 使用するAFKバケットのPC名（部分一致） |
| `--epoch` | | epoch勤務実績入力画面用の入力スクリプトをクリップボードにコピー |

## epoch 勤務実績入力への自動入力

epoch「勤務実績入力」画面の、今日より前で「未登録」の勤務日に次を行います。

1. 始業・終業・休憩（区分「休憩時間」）を入力する。この時点ではサーバーに送らない
2. 確認ダイアログでOKすると、事由「常時ＰＣ未使用者」を事由入力ダイアログ経由で登録する
3. 黄色の欄を確認してから、各行の「登録」を自分で押す

登録済・申請中の日と、AWに記録がない日には触れません。所定休日でもAWに記録があれば入力します。AWで休憩が見つからない日は、epochの既定の休憩のままにします。

### Safari 拡張機能（ボタンで実行）

epoch の画面下のフッター帯の右寄りに「活動履歴に同期」ボタンが出ます。データはローカルの aw-work-hours サーバーから取るので、`aw-work-hours --html` を起動しておきます（`GET /epoch/YYYY-MM`）。

拡張機能の本体は `extension/`、Safari 用の Xcode プロジェクトは `safari/` です。ビルドとインストール：

```bash
xcodebuild -project "safari/AW Epoch Fill/AW Epoch Fill.xcodeproj" -scheme "AW Epoch Fill" \
  -configuration Release -derivedDataPath build/safari \
  DEVELOPMENT_TEAM=<チームID> CODE_SIGN_STYLE=Automatic -allowProvisioningUpdates build
ditto "build/safari/Build/Products/Release/AW Epoch Fill.app" ~/Applications/"AW Epoch Fill.app"
rm -rf build/safari   # ビルド結果が残ると Safari に同じ機能拡張が2つ並ぶ
open ~/Applications/"AW Epoch Fill.app"
```

初回は Safari の「設定」→「機能拡張」で「AW epoch 自動入力」をオンにし、iweb.is.jp.panasonic.com での利用を許可します。

### コンソールに貼り付けて実行

```bash
aw-work-hours --epoch            # 今月分
aw-work-hours --epoch -m last    # 先月分
```

コピーされたスクリプトを、epoch の画面の開発者ツールのコンソールに貼り付けて実行します。

## 勤務日の判定ルール

- 継続している勤務は何時までも同じ日として扱う
- 5:00-8:00の間に新たに開始した勤務は新しい日として扱う
- 24:00をまたいだ場合は26:00のような表記になる

## 設定

AFKバケットはActivityWatch APIから自動検出されます。

休憩とみなす離席の最短時間は `~/.config/aw-work-hours/settings.json` で調整できます（HTML表示と `--epoch` の両方に効きます）：

```json
{
  "break_minutes": 15,
  "core_break_minutes": 30,
  "core_hours": "09:00-18:00"
}
```

`core_hours` の時間帯に始まった離席は `core_break_minutes` 分以上、それ以外は `break_minutes` 分以上で休憩とみなします。

必要に応じてスクリプト内の以下の定数を変更できます：

```python
_WORK_GAP_SECONDS = 3 * 60 * 60  # 3時間以上の離席で別の勤務とみなす
```

## ライセンス

MIT
