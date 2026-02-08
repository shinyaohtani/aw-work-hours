#!/usr/bin/env python3
"""HTML出力とstdout出力の比較テスト"""

import subprocess
import json
import sys

def get_stdout_output(month: str) -> list[str]:
    """Python版の出力を取得"""
    result = subprocess.run(
        ["./aw-work-hours", "--no-colon", f"--month={month}"],
        capture_output=True,
        text=True
    )
    lines = []
    for line in result.stdout.strip().split("\n"):
        if line:
            lines.append(line)
    return lines

def main():
    months = ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"]
    
    print("=== Python版出力（正解データ） ===")
    all_outputs = {}
    for month in months:
        print(f"\n--- {month} ---")
        lines = get_stdout_output(month)
        all_outputs[month] = lines
        for line in lines:
            print(line)
    
    # JSON形式で保存（JavaScriptテスト用）
    with open("/tmp/expected_output.json", "w") as f:
        json.dump(all_outputs, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n正解データを /tmp/expected_output.json に保存しました")
    print(f"このデータをHTML版のJavaScriptと比較してください")

if __name__ == "__main__":
    main()
