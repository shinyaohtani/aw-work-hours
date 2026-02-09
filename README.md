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

## 勤務日の判定ルール

- 継続している勤務は何時までも同じ日として扱う
- 5:00-8:00の間に新たに開始した勤務は新しい日として扱う
- 24:00をまたいだ場合は26:00のような表記になる

## 設定

AFKバケットはActivityWatch APIから自動検出されます。

必要に応じてスクリプト内の以下の定数を変更できます：

```python
_WORK_GAP_SECONDS = 3 * 60 * 60  # 3時間以上の離席で別の勤務とみなす
```

## ライセンス

MIT
