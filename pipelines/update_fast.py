"""高頻度で回す軽量パイプライン: 警報注意報 + アメダス実況(現在の状況)。

どちらも気象庁のAPIだけを叩くのでOpen-Meteoの日次上限(10,000回/日)には一切影響しない。
想定運用: これをGitHub Actionsで5分おき(cronの技術的な最短間隔)に実行してできるだけ
リアルタイムに近づける。天気予報テキストやOpen-Meteoデータ(update_slow.py)は
別スケジュール(2時間おき)で回す。
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
    # 警報注意報(58 office ぶん)
    for pref in PREFECTURES:
        code = pref["code"]
        run([sys.executable, str(ROOT / "warning/fetch_warning.py"), code,
             "--out", str(WEB_DATA / f"warning/{code}.json")])
        time.sleep(0.2)

    # アメダス実況(全国ぶん1ファイル、「現在の状況」欄の気温・降水・湿度)
    run([sys.executable, str(ROOT / "amedas/fetch_amedas_current.py"),
         "--out", str(WEB_DATA / "amedas-current.json")])

    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
