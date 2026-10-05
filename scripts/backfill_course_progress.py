# -*- coding: utf-8 -*-
"""CLI: owner_qa disk course counts → HQ. Default dry-run."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from course_progress_sync import backfill_course_progress, snapshot_owner_qa_dir  # noqa: E402
from owner_qa_log import _data_dir  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--snapshot", action="store_true")
    args = ap.parse_args()
    if args.snapshot:
        dest = _data_dir().parent / f"owner_qa_snapshot_{time.strftime('%Y%m%d_%H%M%S')}"
        print(json.dumps(snapshot_owner_qa_dir(dest), ensure_ascii=False, indent=2))
    report = backfill_course_progress(apply=bool(args.apply))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.apply and report.get("pushed_fail"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
