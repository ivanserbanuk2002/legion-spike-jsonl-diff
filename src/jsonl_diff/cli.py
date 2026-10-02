import argparse
import json
from pathlib import Path

from .compare import compare_records, parse_records


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare local JSONL snapshots")
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--key", default="id")
    parser.add_argument("--ignore-field", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        left = parse_records(args.left.read_text(encoding="utf-8"), args.key)
        right = parse_records(args.right.read_text(encoding="utf-8"), args.key)
        report = compare_records(left, right, args.ignore_field)
        rendered = json.dumps(report, sort_keys=True, allow_nan=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(rendered)
        else:
            print(rendered, end="")
    except (OSError, ValueError, RecursionError) as error:
        parser.error(str(error))
    counts = report["counts"]
    return int(bool(counts["added"] or counts["removed"] or counts["changed"]))


if __name__ == "__main__":
    raise SystemExit(main())
