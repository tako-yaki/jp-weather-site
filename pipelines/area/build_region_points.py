"""一次細分区分(class10)ごとの代表アメダス地点・緯度経度を求めて region_points.json に書き出す。

各officeの短期予報テキストは複数のclass10区分(例: 東京地方/伊豆諸島北部/伊豆諸島南部/小笠原諸島)を
含むことが多いが、気温観測地点(アメダス)との対応は短期予報JSON自体には明示されていない。
一方、週間予報の気温シリーズ(timeSeries[1])はclass10と同じ並び順のアメダス地点リストになっている
ことを確認済みなので、天気文と同じ「週間予報側の対応するインデックス」を使って気温観測地点を選ぶ
(apps/web/src/pages/[code].astro の findWeeklyIndex と同じロジックをPythonで再実装している)。

出力先の緯度経度は、このアメダス地点をOpen-Meteoの取得点として使うためのもの。
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_weekly_index(weekly_areas: list, class10_code: str, class10_name: str) -> int:
    for i, a in enumerate(weekly_areas):
        if a["area"]["code"] == class10_code:
            return i
    for i, a in enumerate(weekly_areas):
        if class10_name.startswith(a["area"]["name"]):
            return i
    return 0


def resolve_amedas_code(pref: dict, weekly_temp_areas: list, weekly_idx: int) -> str | None:
    if pref.get("tempAreaCode"):
        for a in weekly_temp_areas:
            if a["area"]["code"] == pref["tempAreaCode"]:
                return a["area"]["code"]
    if weekly_temp_areas:
        idx = weekly_idx if weekly_idx < len(weekly_temp_areas) else 0
        return weekly_temp_areas[idx]["area"]["code"]
    return None


def dms_to_decimal(dms) -> float | None:
    if not dms:
        return None
    degrees, minutes = dms
    return degrees + minutes / 60


def build(prefectures: list, web_data: Path, amedas_table: dict) -> list:
    points = []
    for pref in prefectures:
        code = pref["code"]
        forecast_source = pref.get("forecastSource", code)
        forecast = json.loads((web_data / f"forecast/{forecast_source}.json").read_text(encoding="utf-8"))

        short_areas = forecast[0]["timeSeries"][0]["areas"]
        weekly_areas = forecast[1]["timeSeries"][0]["areas"]
        weekly_temp_areas = forecast[1]["timeSeries"][1]["areas"]

        target_areas = short_areas
        if pref.get("forecastAreaCode"):
            target_areas = [a for a in short_areas if a["area"]["code"] == pref["forecastAreaCode"]]

        for area in target_areas:
            class10_code = area["area"]["code"]
            class10_name = area["area"]["name"]
            weekly_idx = find_weekly_index(weekly_areas, class10_code, class10_name)
            amedas_code = resolve_amedas_code(pref, weekly_temp_areas, weekly_idx)

            lat = lon = None
            station_name = None
            if amedas_code and amedas_code in amedas_table:
                station = amedas_table[amedas_code]
                lat = dms_to_decimal(station.get("lat"))
                lon = dms_to_decimal(station.get("lon"))
                station_name = station.get("kjName")
            if lat is None or lon is None:
                # フォールバック: officeの代表地点座標
                lat, lon = pref["lat"], pref["lon"]

            points.append(
                {
                    "code": class10_code,
                    "name": class10_name,
                    "officeCode": code,
                    "amedasCode": amedas_code,
                    "amedasName": station_name,
                    "lat": lat,
                    "lon": lon,
                }
            )
    return points


def main() -> None:
    parser = argparse.ArgumentParser(description="class10ごとの代表地点(アメダス)を求める")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    prefectures = json.loads((ROOT / "common/prefectures.json").read_text(encoding="utf-8"))
    amedas_table = json.loads((ROOT / "common/amedastable.json").read_text(encoding="utf-8"))
    web_data = ROOT.parent / "apps/web/public/data"

    points = build(prefectures, web_data, amedas_table)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(points, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out} ({len(points)} regions)", file=sys.stderr)


if __name__ == "__main__":
    main()
