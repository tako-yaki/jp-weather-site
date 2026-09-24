"""気象庁の防災情報JSON APIから地域予報データを取得する。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

JMA_FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"


def fetch_forecast(area_code: str) -> list:
    return fetch_json(JMA_FORECAST_URL.format(area_code=area_code))


def main() -> None:
    parser = argparse.ArgumentParser(description="JMA forecast fetcher")
    parser.add_argument("area_code", help="気象庁の地域コード (例: 130000 = 東京都)")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    args = parser.parse_args()

    data = fetch_forecast(args.area_code)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
