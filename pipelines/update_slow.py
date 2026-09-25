"""低頻度で回すパイプライン: 予報テキスト + 地域の代表地点(緯度経度)算出。

Open-Meteoはここでは一切呼ばない。時系列グラフ・日の出日の入り・10日間予報の7〜10日目・
市区町村の気温は、いずれもブラウザ側が地域/市区町村の緯度経度を使って直接Open-Meteoへ
取得する方式にしたため(pipelineのOpen-Meteo無料枠を一切消費しない)。
このスクリプトが担うのは「地域ごとにどの緯度経度を使うか」を算出することだけで、
region-points.json として apps/web/public/data に書き出し、Astroがビルド時にページへ埋め込む。

リビルドが必要なのは実質ここで更新するJMAの予報テキストだけになる。JMA自体が
1日に数回しか予報テキストを更新しないため、2〜3時間おきの実行で十分新鮮。
Cloudflare Pagesの無料枠(月500ビルド)に対し、2時間おき=1日12回×30日=360回(72%)。

警報注意報とアメダス実況はこちらでは触らない(update_fast.py が5分おきに別途更新する)。
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB_DATA = ROOT.parent / "apps/web/public/data"
PREFECTURES = json.loads((ROOT / "common/prefectures.json").read_text(encoding="utf-8"))


def run(args: list[str]) -> None:
    print("$", " ".join(args), file=sys.stderr)
    subprocess.run(args, check=True)


def main() -> None:
    # 1. 気象庁の予報テキスト(office単位、58ぶん)
    for pref in PREFECTURES:
        code = pref["code"]
        # 十勝地方・奄美地方は自前の予報JSONを持たず、隣接officeのJSONに間借りしているため、
        # forecastSourceが指定されていればそちらのコードで取得する(出力先は自分のcodeのまま)。
        forecast_source = pref.get("forecastSource", code)
        print(f"--- {pref['name']} ({code}) ---", file=sys.stderr)
        run([sys.executable, str(ROOT / "forecast/fetch_forecast.py"), forecast_source,
             "--out", str(WEB_DATA / f"forecast/{code}.json")])
        time.sleep(0.2)

    # 2. アメダス地点マスタ(緯度経度)を最新化してから、一次細分区分ごとの代表地点(緯度経度)を
    #    算出してapps/web/public/dataへ書き出す(Astroがビルド時に読み、クライアント側の
    #    Open-Meteo取得先としてページへ埋め込む)。地点算出には各officeの予報JSON(1で取得済み)が
    #    必要なので、この順番でなければならない。
    run([sys.executable, str(ROOT / "amedas/fetch_amedas_table.py"),
         "--out", str(ROOT / "common/amedastable.json")])
    run([sys.executable, str(ROOT / "area/build_region_points.py"),
         "--out", str(WEB_DATA / "region-points.json")])

    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
