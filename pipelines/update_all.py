"""47都道府県ぶんの全データソースをまとめて取得し、apps/web/public/data に書き込む。"""
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
    for pref in PREFECTURES:
        code, lat, lon = pref["code"], str(pref["lat"]), str(pref["lon"])
        print(f"--- {pref['name']} ({code}) ---", file=sys.stderr)
        run([sys.executable, str(ROOT / "forecast/fetch_forecast.py"), code,
             "--out", str(WEB_DATA / f"forecast/{code}.json")])
        run([sys.executable, str(ROOT / "warning/fetch_warning.py"), code,
             "--out", str(WEB_DATA / f"warning/{code}.json")])
        run([sys.executable, str(ROOT / "openmeteo/fetch_openmeteo.py"), lat, lon,
             "--out", str(WEB_DATA / f"openmeteo/{code}.json")])
        run([sys.executable, str(ROOT / "openmeteo/fetch_openmeteo_extended.py"), lat, lon,
             "--out", str(WEB_DATA / f"openmeteo/daily-{code}.json")])
        time.sleep(0.2)
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
