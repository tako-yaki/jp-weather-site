"""ローカルでの手動一括更新用: update_fast.py + update_slow.py を続けて実行する。

Open-Meteoは呼ばない(時系列グラフ・10日間予報の参考日・市区町村の気温はいずれも
ブラウザ側が直接取得するため、pipeline側でのOpen-Meteo取得は不要になった)。
本番のGitHub Actionsでは、更新頻度が異なるこの2つを別々のスケジュールで実行する
(update_fast.py: 警報注意報+アメダス実況、5分おき / update_slow.py: 予報テキスト+地域の
代表地点算出、2時間おき)。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(args: list[str]) -> None:
    print("$", " ".join(args), file=sys.stderr)
    subprocess.run(args, check=True)


def main() -> None:
    run([sys.executable, str(ROOT / "update_slow.py")])
    run([sys.executable, str(ROOT / "update_fast.py")])
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
