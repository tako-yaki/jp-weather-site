"""Open-Meteoから10日間予報の8〜10日目を補うための、長期の日別データを取得する。
気象庁の週間予報は7日先までしか出ないため、それより先の参考値として使う
（このデータには気象庁の「確度」に相当する情報はない）。
"""
import argparse
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

BASE_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_PARAMS = "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"


def fetch_openmeteo_daily(lat: str, lon: str, forecast_days: int) -> dict:
    query = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "daily": DAILY_PARAMS,
            "timezone": "Asia/Tokyo",
            "forecast_days": forecast_days,
        }
    )
    return fetch_json(f"{BASE_URL}?{query}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Open-Meteo (長期日別、10日間予報の補完用) fetcher")
    parser.add_argument("lat", help="緯度 (例: 35.6762 = 東京)")
    parser.add_argument("lon", help="経度 (例: 139.6503 = 東京)")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    parser.add_argument("--forecast-days", type=int, default=12)
    args = parser.parse_args()

    data = fetch_openmeteo_daily(args.lat, args.lon, args.forecast_days)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
