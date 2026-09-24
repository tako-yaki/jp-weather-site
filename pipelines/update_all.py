"""ローカル開発用: 東京の全データソースをまとめて取得し、apps/web/public/data に書き込む。
地点が東京固定なのは、まだ地点検索機能を実装していないため。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB_DATA = ROOT.parent / "apps/web/public/data"

AREA_CODE = "130000"
LAT, LON = "35.6762", "139.6503"


def run(args: list[str]) -> None:
    print("$", " ".join(args), file=sys.stderr)
    subprocess.run(args, check=True)


def main() -> None:
    run([sys.executable, str(ROOT / "forecast/fetch_forecast.py"), AREA_CODE,
         "--out", str(WEB_DATA / f"forecast/{AREA_CODE}.json")])
    run([sys.executable, str(ROOT / "warning/fetch_warning.py"), AREA_CODE,
         "--out", str(WEB_DATA / f"warning/{AREA_CODE}.json")])
    run([sys.executable, str(ROOT / "openmeteo/fetch_openmeteo.py"), LAT, LON,
         "--out", str(WEB_DATA / f"openmeteo/{AREA_CODE}.json")])
    run([sys.executable, str(ROOT / "openmeteo/fetch_openmeteo_extended.py"), LAT, LON,
         "--out", str(WEB_DATA / f"openmeteo/daily-{AREA_CODE}.json")])
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
