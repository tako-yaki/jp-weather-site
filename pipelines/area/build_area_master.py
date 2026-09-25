"""気象庁 area.json から、予報区の階層(office/class10/class15/class20)と
都道府県ごとのoffice一覧(北海道・鹿児島県・奄美地方除く・沖縄県は複数officeに分割)を
まとめた area-master.json を生成する。

市区町村単位の警報表示や、地点選択UIのグループ化に使う。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

AREA_JSON_URL = "https://www.jma.go.jp/bosai/common/const/area.json"

# 気象庁のofficeは基本的に1都道府県=1officeだが、以下の3県だけ複数officeに分かれている。
# (area.jsonのoffice名がそのまま都道府県名と一致するかどうかで自動判定できないのはこの3県だけ、
#  というのは実データを取得して全58officeぶん確認済み)
SPLIT_PREFECTURES = {
    "北海道": [
        "011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000",
    ],
    "鹿児島県": ["460040", "460100"],
    "沖縄県": ["471000", "472000", "473000", "474000"],
}


def build(area: dict) -> dict:
    offices = area["offices"]
    split_codes = {code for codes in SPLIT_PREFECTURES.values() for code in codes}

    prefecture_groups = list(SPLIT_PREFECTURES.items())
    for code, office in offices.items():
        if code in split_codes:
            continue
        prefecture_groups.append((office["name"], [code]))

    return {
        "offices": {
            code: {"name": v["name"], "officeName": v.get("officeName", ""), "parent": v["parent"]}
            for code, v in offices.items()
        },
        "class10s": {
            code: {"name": v["name"], "parent": v["parent"]} for code, v in area["class10s"].items()
        },
        "class15s": {
            code: {"name": v["name"], "parent": v["parent"]} for code, v in area["class15s"].items()
        },
        "class20s": {
            code: {"name": v["name"], "parent": v["parent"]} for code, v in area["class20s"].items()
        },
        "prefectureGroups": [
            {"name": name, "officeCodes": codes} for name, codes in prefecture_groups
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="気象庁area.jsonから予報区マスタを生成する")
    parser.add_argument("--out", required=True, help="出力先のJSONファイルパス")
    args = parser.parse_args()

    area = fetch_json(AREA_JSON_URL)
    result = build(area)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
