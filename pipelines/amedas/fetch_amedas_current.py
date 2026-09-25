"""アメダスの最新の実況値(全国ぶん)を取得する。

latest_time.txt で最新観測時刻を確認し、その時刻の map/{time}.json を取得する。
全国1000地点超のデータが1ファイルに入っているので、そのまま保存して
Astro側で地点コードをキーに引く。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

LATEST_TIME_URL = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
AMEDAS_MAP_URL = "https://www.jma.go.jp/bosai/amedas/data/map/{stamp}.json"


def main() -> None:
    import urllib.request

    parser = argparse.ArgumentParser(description="AMeDAS latest observation fetcher")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    args = parser.parse_args()

    req = urllib.request.Request(LATEST_TIME_URL, headers={"User-Agent": "weather-site-dev/0.1 (local pipeline)"})
    with urllib.request.urlopen(req, timeout=10) as res:
        latest_time = res.read().decode("utf-8").strip()

    # "2026-09-25T14:00:00+09:00" -> "20260925140000"
    date_part, time_part = latest_time.split("T")
    time_part = time_part.split("+")[0].split("-")[0]
    stamp = date_part.replace("-", "") + time_part.replace(":", "")

    data = fetch_json(AMEDAS_MAP_URL.format(stamp=stamp))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps({"observedAt": latest_time, "stations": data}, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"saved: {args.out} (observedAt={latest_time})", file=sys.stderr)


if __name__ == "__main__":
    main()
