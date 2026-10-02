import json
import math
from collections.abc import Iterable


def _reject_constant(value: str) -> None:
    raise ValueError("nonstandard JSON number")


def parse_records(text: str, key: str = "id") -> dict[str, dict]:
    if not isinstance(key, str) or not key.strip():
        raise ValueError("key must be a nonblank field name")
    records = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line, parse_constant=_reject_constant)
        except (ValueError, RecursionError) as error:
            raise ValueError(f"line {line_number}: invalid JSON") from error
        if not isinstance(record, dict):
            raise ValueError(f"line {line_number}: expected an object")
        pending = [record]
        while pending:
            value = pending.pop()
            if isinstance(value, dict):
                pending.extend(value.values())
            elif isinstance(value, list):
                pending.extend(value)
            elif isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"line {line_number}: nonfinite number")
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"line {line_number}: expected a nonblank string key")
        if identifier in records:
            raise ValueError(f"line {line_number}: duplicate record key")
        records[identifier] = record
    return records


def compare_records(left: dict[str, dict], right: dict[str, dict],
                    ignore_fields: Iterable[str] = ()) -> dict:
    ignored = set(ignore_fields)
    if any(not isinstance(field, str) or not field.strip() for field in ignored):
        raise ValueError("ignored fields must have nonblank names")
    added = [key for key in right if key not in left]
    removed = [key for key in left if key not in right]
    changed = []
    for key, before in left.items():
        if key not in right:
            continue
        after = right[key]
        fields = []
        for field in sorted((before.keys() | after.keys()) - ignored):
            if field not in before or field not in after:
                fields.append(field)
            elif json.dumps(before[field], sort_keys=True) != json.dumps(after[field], sort_keys=True):
                fields.append(field)
        if fields:
            changed.append({"key": key, "fields": fields})
    return {"added": added, "removed": removed, "changed": changed,
            "counts": {"added": len(added), "removed": len(removed), "changed": len(changed),
                       "unchanged": len(left.keys() & right.keys()) - len(changed)}}
