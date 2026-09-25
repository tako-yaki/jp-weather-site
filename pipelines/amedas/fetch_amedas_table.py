"""アメダス観測地点マスタ(緯度経度など)を取得する。地点は基本的に変わらないので、
実行のたびに最新化しておけば十分(専用のバージョン管理はしない)。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

AMEDAS_TABLE_URL = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="AMeDAS station master fetcher")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    args = parser.parse_args()

    data = fetch_json(AMEDAS_TABLE_URL)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
