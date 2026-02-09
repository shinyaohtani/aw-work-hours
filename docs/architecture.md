# Architecture

## Class Diagram (17 classes)

```mermaid
flowchart TD
    START(["$ aw-work-hours"]) --> CLIMain

    subgraph cli["CLI Layer"]
        CLIMain["CLIMain<br/><small>メインCLI処理</small>"]
        CLIArgs["CLIArgs<br/><small>コマンドライン引数</small>"]
        CLIMain --> CLIArgs
    end

    CLIMain -->|set_preference| AFKBucket

    subgraph bucket["Bucket Resolution"]
        AFKBucket["AFKBucket<br/><small>AFKバケット</small>"]
        AFKBucketCandidates["AFKBucketCandidates<br/><small>バケット候補群</small>"]
        AFKBucket -->|"候補から選択"| AFKBucketCandidates
    end

    CLIMain -->|"text / csv"| CLIOutput
    CLIMain -->|"--html"| WorkHTTPServer

    subgraph text_csv["Text / CSV Mode"]
        CLIOutput["CLIOutput<br/><small>出力振り分け</small>"]
        WorkCSV["WorkCSV<br/><small>CSV出力</small>"]
        WorkText["WorkText<br/><small>テキスト出力</small>"]
        CLIOutput -->|"-o file"| WorkCSV
        CLIOutput -->|"stdout"| WorkText
    end

    subgraph html["HTML Mode"]
        WorkHTTPServer["WorkHTTPServer<br/><small>HTTPサーバー</small>"]
        WorkHTTPHandler["WorkHTTPHandler<br/><small>リクエストハンドラ</small>"]
        WorkHTMLTemplate["WorkHTMLTemplate<br/><small>HTMLテンプレート</small>"]
        WorkHTMLResponse["WorkHTMLResponse<br/><small>APIレスポンス生成</small>"]
        WorkHTMLRow["WorkHTMLRow<br/><small>HTML行データ</small>"]
        WorkHTTPServer -->|"HTML render"| WorkHTMLTemplate
        WorkHTTPServer -->|"HTTPサーバー起動"| WorkHTTPHandler
        WorkHTTPHandler -->|"/data/{month}"| WorkHTMLResponse
        WorkHTMLResponse -->|"行生成"| WorkHTMLRow
    end

    subgraph shared["Shared Data Processing"]
        MonthPeriod["MonthPeriod<br/><small>月の期間・日付範囲</small>"]
        AFKEvents["AFKEvents<br/><small>AFKイベント取得</small>"]
        WorkCalendar["WorkCalendar<br/><small>勤務カレンダー</small>"]
        DailyWork["DailyWork<br/><small>日ごとの勤務統計</small>"]
        HolidayCalendar["HolidayCalendar<br/><small>祝日カレンダー</small>"]
        DailyWork -.->|"work_date()"| WorkCalendar
    end

    AFKEvents -->|"bucket id"| AFKBucket

    %% Text/CSV mode → shared
    CLIMain -->|"parse / fetch"| MonthPeriod & AFKEvents
    WorkCSV -->|"date_range()"| MonthPeriod
    WorkText -->|"date_range()"| MonthPeriod
    WorkText -->|"is_holiday()"| HolidayCalendar

    %% HTML mode → shared
    WorkHTMLResponse -->|"parse / fetch"| MonthPeriod & AFKEvents
    WorkHTMLResponse -->|"is_holiday()"| HolidayCalendar

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
        B1["AFKEvents<br/>イベント取得"]
    end

    subgraph process["3. Process"]
        C1["WorkCalendar<br/>from work_blocks"]
        C2["DailyWork<br/>from raw events"]
        C3["HolidayCalendar<br/>祝日判定"]
    end

    subgraph output["4. Output"]
        D1["WorkText<br/>テキスト"]
        D2["WorkCSV<br/>CSV"]
        D3["WorkHTMLResponse<br/>+ WorkHTMLRow<br/>JSON API"]
    end

    A1 --> A2 & A3
    A2 & A3 --> B1
    B1 --> C1 & C2
    C1 & C2 & C3 --> D1 & D2 & D3
```

## Class Summary

| # | Class | Methods | Role |
|---|-------|---------|------|
| 1 | AFKBucketCandidates | 5 | AFK bucket selection from candidates |
| 2 | AFKBucket | 4 | Bucket ID caching and resolution |
| 3 | MonthPeriod | 5 | Month period parsing and date range generation |
| 4 | AFKEvents | 5 | AFK event fetching and work block extraction |
| 5 | DailyWork | 4 | Daily active time and max gap calculation |
| 6 | HolidayCalendar | 6 | Japanese holiday lookup with file cache |
| 7 | WorkCalendar | 5 | Work calendar from event blocks |
| 8 | WorkCSV | 5 | CSV format output |
| 9 | WorkText | 5 | Text format output |
| 10 | WorkHTMLTemplate | 5 | HTML page template (CSS/JS/controls) |
| 11 | WorkHTMLRow | 6 | Per-day row data for HTML |
| 12 | WorkHTMLResponse | 4 | JSON API response for HTML frontend |
| 13 | WorkHTTPHandler | 5 | HTTP request routing and proxy |
| 14 | WorkHTTPServer | 5 | HTTP server lifecycle management |
| 15 | CLIArgs | 8 | CLI argument parsing and properties |
| 16 | CLIOutput | 4 | Output dispatch (CSV or text) |
| 17 | CLIMain | 5 | Application entry point |
