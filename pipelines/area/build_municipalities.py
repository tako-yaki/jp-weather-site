"""市区町村(二次細分区分 class20)ごとの代表地点(緯度経度)を作る。

気象庁 area.json 自体には緯度経度が無いため、総務省の住所データを整備した
geolonia/japanese-addresses (municipality単位まで集計可能なオープンデータ、CC BY 4.0)
から市区町村ごとの町丁目レベル座標を集計し、その重心を代表地点として使う。

名前の突き合わせルール(実データで確認済み: 1805件中1793件=99.3%が解決できる):
  1. 完全一致 (都道府県, 市区町村名)
  2. 「◯◯郡△△町」のように郡名が付く場合、郡名を除いた短縮名でも一致を試す
  3. 前方一致 (JMAの区分名が、政令指定都市の区名などの接頭辞になっているケース)
  4. 逆前方一致 (「釧路市釧路」のような合併前の旧市町村名を使ったJMAの細分)
残りの約12件(政令指定都市を東西南北で分割するJMA独自区分、および地理データが
そもそも存在しない一部離島の村)は解決できないため出力に含めない。該当するUIは
そのまま親区分(class10)のデータにフォールバックする(既存動作から後退しない)。
"""
import argparse
import csv
import io
import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json, USER_AGENT

AREA_JSON_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
GEOLONIA_CSV_URL = "https://raw.githubusercontent.com/geolonia/japanese-addresses/master/data/latest.csv"

# office → 都道府県名。北海道・鹿児島県・沖縄県だけ複数officeに分かれる
# (build_area_master.py の SPLIT_PREFECTURES と同じ実データ確認済みの対応)。
SPLIT_PREFECTURES = {
    "北海道": ["011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000"],
    "鹿児島県": ["460040", "460100"],
    "沖縄県": ["471000", "472000", "473000", "474000"],
}
OFFICE_TO_SPLIT_PREF = {code: pref for pref, codes in SPLIT_PREFECTURES.items() for code in codes}


def normalize(name: str) -> str:
    return name.replace("ヶ", "ケ").replace("ヵ", "カ")


def fetch_csv_rows(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as res:
        text = res.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def build(area: dict, geo_rows: list[dict]) -> dict:
    offices = area["offices"]
    c10, c15, c20 = area["class10s"], area["class15s"], area["class20s"]

    def office_pref(office_code: str) -> str:
        return OFFICE_TO_SPLIT_PREF.get(office_code, offices[office_code]["name"])

    def class20_pref(code: str) -> str:
        office_code = c10[c15[c20[code]["parent"]]["parent"]]["parent"]
        return office_pref(office_code)

    # 市区町村名ごとに、その町丁目座標をすべて集めて重心を出す
    points: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in geo_rows:
        lat, lon = row["緯度"], row["経度"]
        if not lat or not lon:
            continue
        key = (row["都道府県名"], normalize(row["市区町村名"]))
        points[key].append((float(lat), float(lon)))

    # 「◯◯郡△△町」→ 郡名を除いた短縮名の索引も作る
    short_names: dict[tuple[str, str], list[str]] = defaultdict(list)
    all_names_by_pref: dict[str, set] = defaultdict(set)
    for pref, name in points:
        all_names_by_pref[pref].add(name)
        if "郡" in name:
            short = name.split("郡", 1)[-1]
            short_names[(pref, short)].append(name)
            all_names_by_pref[pref].add(short)

    def centroid(pref: str, names: list[str]) -> tuple[float, float]:
        # namesには短縮名(郡名なし)が混ざりうるので、points索引にある正式名へ展開してから集める
        full_names = [n for name in names for n in (short_names.get((pref, name)) or [name])]
        pts = [p for n in full_names for p in points[(pref, n)]]
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    result = {}
    unresolved = []
    for code, v in c20.items():
        pref = class20_pref(code)
        name = normalize(v["name"])

        if (pref, name) in points:
            lat, lon = centroid(pref, [name])
        elif (pref, name) in short_names:
            lat, lon = centroid(pref, short_names[(pref, name)])
        else:
            fwd = [n for n in all_names_by_pref[pref] if n.startswith(name)]
            rev = [n for n in all_names_by_pref[pref] if len(n) >= 2 and name.startswith(n)]
            candidates = fwd or rev
            if not candidates:
                unresolved.append((code, pref, v["name"]))
                continue
            lat, lon = centroid(pref, candidates)

        result[code] = {"lat": round(lat, 5), "lon": round(lon, 5)}

    print(f"resolved {len(result)}/{len(c20)} municipalities", file=sys.stderr)
    if unresolved:
        print(f"unresolved ({len(unresolved)}), falls back to parent-level data:", file=sys.stderr)
        for code, pref, name in unresolved:
            print(f"  {code} {pref}{name}", file=sys.stderr)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="市区町村(class20)ごとの代表地点(緯度経度)を作る")
    parser.add_argument("--out", required=True, help="出力先のJSONファイルパス")
    args = parser.parse_args()

    area = fetch_json(AREA_JSON_URL)
    geo_rows = fetch_csv_rows(GEOLONIA_CSV_URL)
    result = build(area, geo_rows)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
