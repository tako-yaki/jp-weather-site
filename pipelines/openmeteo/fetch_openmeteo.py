"""Open-Meteoから現在の状況・時間別予報・当面の日の出日の入りを取得する。"""
import argparse
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

BASE_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_PARAMS = "temperature_2m,relative_humidity_2m,precipitation,weathercode"
HOURLY_PARAMS = "temperature_2m,precipitation,weathercode"
DAILY_PARAMS = "sunrise,sunset,temperature_2m_max,temperature_2m_min"


def fetch_openmeteo(lat: str, lon: str, forecast_days: int = 3) -> dict:
    query = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "current": CURRENT_PARAMS,
            "hourly": HOURLY_PARAMS,
            "daily": DAILY_PARAMS,
            "timezone": "Asia/Tokyo",
            "forecast_days": forecast_days,
        }
    )
    return fetch_json(f"{BASE_URL}?{query}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Open-Meteo (現在・時間別・短期日別) fetcher")
    parser.add_argument("lat", help="緯度 (例: 35.6762 = 東京)")
    parser.add_argument("lon", help="経度 (例: 139.6503 = 東京)")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    parser.add_argument("--forecast-days", type=int, default=3)
    args = parser.parse_args()

    data = fetch_openmeteo(args.lat, args.lon, args.forecast_days)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
