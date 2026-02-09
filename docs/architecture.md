# Architecture

## File Sections

```
TYPES   — CLIError / APIConnectionError / AWEvent / HTMLEvent
DOMAIN  — WorkRule / MonthPeriod / AFKBucketCandidates / AFKBucket / AFKEvents / HolidayCalendar / DailyWork / WorkCalendar
OUTPUT  — WorkCSV / WorkText
WEB     — WorkHTMLRow / WorkHTMLResponse / WorkHTTPHandler / WorkHTTPServer / WorkHTMLTemplate
CLI     — CLIArgs / CLIOutput / CLIMain
```

## Class Diagram (18 classes + 4 types)

```mermaid
flowchart TD
    START(["$ aw-work-hours"]) --> CLIMain

    subgraph cli["CLI Layer"]
        CLIMain["CLIMain<br/><small>メインCLI処理</small>"]
        CLIArgs["CLIArgs<br/><small>コマンドライン引数</small>"]
        CLIOutput["CLIOutput<br/><small>出力振り分け</small>"]
        CLIMain --> CLIArgs
        CLIMain -->|"text / csv"| CLIOutput
    end

    CLIMain -->|set_preference| AFKBucket
    CLIMain -->|"--html"| WorkHTTPServer

    subgraph types["Types"]
        CLIError["CLIError<br/><small>ユーザー入力エラー</small>"]
        APIConnectionError["APIConnectionError<br/><small>API接続エラー</small>"]
        AWEvent["AWEvent<br/><small>AFKイベント型</small>"]
        HTMLEvent["HTMLEvent<br/><small>HTMLイベント型</small>"]
    end

    subgraph domain["Domain"]
        WorkRule["WorkRule<br/><small>勤務仕様ルール</small>"]
        MonthPeriod["MonthPeriod<br/><small>月の期間・日付範囲</small>"]
        AFKBucketCandidates["AFKBucketCandidates<br/><small>バケット候補群</small>"]
        AFKBucket["AFKBucket<br/><small>AFKバケット</small>"]
        AFKEvents["AFKEvents<br/><small>AFKイベント取得</small>"]
        HolidayCalendar["HolidayCalendar<br/><small>祝日カレンダー</small>"]
        DailyWork["DailyWork<br/><small>日ごとの勤務統計</small>"]
        WorkCalendar["WorkCalendar<br/><small>勤務カレンダー</small>"]
        AFKBucket -->|"候補から選択"| AFKBucketCandidates
        AFKEvents -->|"ルール参照"| WorkRule
        DailyWork -.->|"work_date()"| WorkRule
        WorkCalendar -.->|"work_date()"| WorkRule
        WorkCalendar -->|"from_period()"| AFKEvents & DailyWork
    end

    subgraph output["Output"]
        WorkCSV["WorkCSV<br/><small>CSV出力</small>"]
        WorkText["WorkText<br/><small>テキスト出力</small>"]
        CLIOutput -->|"-o file"| WorkCSV
        CLIOutput -->|"stdout"| WorkText
    end

    subgraph web["Web"]
        WorkHTTPServer["WorkHTTPServer<br/><small>HTTPサーバー</small>"]
        WorkHTTPHandler["WorkHTTPHandler<br/><small>リクエストハンドラ</small>"]
        WorkHTMLTemplate["WorkHTMLTemplate<br/><small>HTMLテンプレート</small>"]
        WorkHTMLResponse["WorkHTMLResponse<br/><small>APIレスポンス生成</small>"]
        WorkHTMLRow["WorkHTMLRow<br/><small>HTML行データ</small>"]
        WorkHTTPServer -->|"HTTPサーバー起動"| WorkHTTPHandler
        WorkHTTPHandler -->|"/data/{month}"| WorkHTMLResponse
        WorkHTMLResponse -->|"行生成"| WorkHTMLRow
    end

    CLIMain -->|"render()"| WorkHTMLTemplate
    CLIMain -->|"html: str"| WorkHTTPServer

    AFKEvents -->|"bucket id"| AFKBucket

    %% Domain dependencies
    CLIMain -->|"from_period()"| WorkCalendar
    WorkCSV -->|"date_range()"| MonthPeriod
    WorkText -->|"date_range()"| MonthPeriod
    WorkText -->|"is_holiday()"| HolidayCalendar
    WorkCSV -->|"adjusted_hour()"| WorkRule
    WorkText -->|"adjusted_hour()"| WorkRule

    %% HTML mode → domain
    WorkHTMLResponse -->|"from_period()"| WorkCalendar
    WorkHTMLResponse -->|"is_holiday()"| HolidayCalendar
    WorkHTMLRow -->|"adjusted_hour()"| WorkRule

    %% Exception flow
    CLIMain -.->|"catch"| CLIError & APIConnectionError

    AW[("ActivityWatch<br/>localhost:5600")]
    HJ[("holidays-jp<br/>API")]
    AFKBucketCandidates -.-> AW
    AFKEvents -.-> AW
    HolidayCalendar -.-> HJ
```

## Processing Flow

```mermaid
flowchart LR
    subgraph input["1. Input"]
        A1["CLIArgs<br/>引数解析"]
        A2["AFKBucket<br/>バケット特定"]
        A3["MonthPeriod<br/>期間特定"]
    end

    subgraph fetch["2. Fetch"]
        B1["WorkCalendar.from_period()<br/>イベント取得+変換"]
    end

    subgraph process["3. Process"]
        C1["WorkCalendar<br/>勤務日マッピング"]
        C2["DailyWork<br/>日別統計"]
        C3["HolidayCalendar<br/>祝日判定"]
        C4["WorkRule<br/>勤務仕様ルール"]
    end

    subgraph output["4. Output"]
        D1["WorkText<br/>テキスト"]
        D2["WorkCSV<br/>CSV"]
        D3["WorkHTMLResponse<br/>+ WorkHTMLRow<br/>JSON API"]
    end

    A1 --> A2 & A3
    A2 & A3 --> B1
    B1 --> C1 & C2
    C1 & C2 & C3 & C4 --> D1 & D2 & D3
```

## Exception Flow

```mermaid
flowchart LR
    subgraph domain["Domain Layer"]
        D1["MonthPeriod<br/>CLIError"]
        D2["AFKBucketCandidates<br/>CLIError"]
        D3["AFKBucket<br/>APIConnectionError"]
        D4["AFKEvents<br/>APIConnectionError"]
    end

    subgraph cli["CLI Layer"]
        C1["CLIMain.run()<br/>catch → stderr + exit(1)"]
    end

    subgraph web["Web Layer"]
        W1["WorkHTTPHandler<br/>catch → send_error(500)"]
    end

    D1 & D2 & D3 & D4 -->|raise| C1
    D3 & D4 -->|raise| W1
```

## Class Summary

| # | Section | Class | Methods | Role |
|---|---------|-------|---------|------|
| - | TYPES | CLIError | - | User input error |
| - | TYPES | APIConnectionError | - | AW API connection error |
| - | TYPES | AWEvent | - | AFK event TypedDict |
| - | TYPES | HTMLEvent | - | HTML event TypedDict |
| 1 | DOMAIN | WorkRule | 4 | Work day boundary, block split, adjusted hour, span |
| 2 | DOMAIN | MonthPeriod | 5 | Month period parsing and date range generation |
| 3 | DOMAIN | AFKBucketCandidates | 5 | AFK bucket selection from candidates |
| 4 | DOMAIN | AFKBucket | 4 | Bucket ID caching and resolution |
| 5 | DOMAIN | AFKEvents | 5 | AFK event fetching and work block extraction |
| 6 | DOMAIN | HolidayCalendar | 6 | Japanese holiday lookup with file cache |
| 7 | DOMAIN | DailyWork | 4 | Daily active time and max gap calculation |
| 8 | DOMAIN | WorkCalendar | 5 | Work calendar from event blocks (+ from_period) |
| 9 | OUTPUT | WorkCSV | 5 | CSV format output |
| 10 | OUTPUT | WorkText | 5 | Text format output |
| 11 | WEB | WorkHTMLRow | 5 | Per-day row data for HTML |
| 12 | WEB | WorkHTMLResponse | 4 | JSON API response for HTML frontend |
| 13 | WEB | WorkHTTPHandler | 6 | HTTP request routing and proxy |
| 14 | WEB | WorkHTTPServer | 6 | HTTP server lifecycle management |
| 15 | WEB | WorkHTMLTemplate | 5 | HTML page template (CSS/JS/controls) |
| 16 | CLI | CLIArgs | 9 | CLI argument parsing and properties |
| 17 | CLI | CLIOutput | 5 | Output dispatch (CSV or text) |
| 18 | CLI | CLIMain | 6 | Application entry point |
