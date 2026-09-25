"""気象庁の防災情報JSON APIから警報注意報データを取得する。

2026年5月29日の防災気象情報の体系変更に伴い、旧エンドポイント
(bosai/warning/data/warning/{code}.json) は実質的に更新が止まっている
(全国どのofficeで確認しても2026年5月時点のデータのまま)。
新エンドポイント (bosai/warning/data/r8/{code}.json) は「直近の発表いくつかぶんの
配信履歴」を配列で返す形式に変わっており、1つの配列要素は特定の現象(例: 乾燥注意報)
だけを更新する差分的な内容のことが多い。そのため、時系列順にマージして
「現在この地域で有効な警報注意報は何か」を再構成する必要がある。

出力の形は、既存のAstro側コード([code].astro)が読んでいる旧フォーマット
(areaTypes[].areas[].{code, warnings:[{code, status}]}) に合わせてある。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.http import fetch_json

JMA_WARNING_R8_URL = "https://www.jma.go.jp/bosai/warning/data/r8/{area_code}.json"

NO_WARNING_STATUS = "発表警報・注意報はなし"


def merge_area_type(reports: list, item_key: str) -> list:
    """reports(reportDatetime昇順)を area_code -> {warning_code: status} にマージする。

    r8のレポート1件は「特定の現象1つぶんの状態変化」を表す配信単位で、その現象に
    関係しない地域には code なしの「発表警報・注意報はなし」が並ぶ(=その現象については
    対象外、という意味であって「この地域は他の現象も含めて何も出ていない」という意味ではない)。
    そのため code なしの kind は無視し(状態をリセットしない)、code ありの kind だけを
    area_code -> {warning_code: status} にマージしていく。ある現象が解除されればcodeは
    残したまま status が「解除」に更新されるので、フロント側の isActiveStatus() で除外できる。
    """
    area_states: dict[str, dict[str, str]] = {}
    all_area_codes: list[str] = []
    seen_area_codes: set[str] = set()

    for report in reports:
        items = report.get("warning", {}).get(item_key, [])
        for item in items:
            area_code = item["areaCode"]
            if area_code not in seen_area_codes:
                seen_area_codes.add(area_code)
                all_area_codes.append(area_code)
            for kind in item.get("kinds", []):
                code = kind.get("code")
                status = kind.get("status")
                if not code or not status:
                    continue
                area_states.setdefault(area_code, {})[code] = status

    result = []
    for area_code in all_area_codes:
        state = area_states.get(area_code, {})
        warnings = [{"code": code, "status": status} for code, status in state.items()]
        if not warnings:
            warnings = [{"status": NO_WARNING_STATUS}]
        result.append({"code": area_code, "warnings": warnings})
    return result


def fetch_warning(area_code: str) -> dict:
    reports = fetch_json(JMA_WARNING_R8_URL.format(area_code=area_code))
    reports_sorted = sorted(reports, key=lambda r: r["reportDatetime"])
    latest = reports_sorted[-1] if reports_sorted else {}

    return {
        "reportDatetime": latest.get("reportDatetime"),
        "headlineText": latest.get("headlineText"),
        "areaTypes": [
            {"areas": merge_area_type(reports_sorted, "class10Items")},
            {"areas": merge_area_type(reports_sorted, "class20Items")},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="JMA warning fetcher (r8)")
    parser.add_argument("area_code", help="気象庁の地域コード (例: 130000 = 東京都)")
    parser.add_argument("--out", type=Path, required=True, help="出力先ファイル")
    args = parser.parse_args()

    data = fetch_warning(args.area_code)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
