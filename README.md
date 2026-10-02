# jsonl-diff

Compare two local JSONL snapshots by a unique string key. Python 3.12, no runtime dependencies or network calls.

```bash
python -m pip install .
jsonl-diff --left data/before.jsonl --right data/after.jsonl --ignore-field observed
```

The synthetic example reports added `c`, removed `b`, and a status change for `a`. Exit 0 means no differences, 1 means differences, and 2 means invalid input or an I/O error. A difference is an expected result, not a failed comparison.

`--key eventId` chooses a field other than the default `id`. Each nonblank line must be an object with a unique nonblank string key. Keys are case-sensitive and are not trimmed. Missing or duplicate keys and nonfinite numbers are rejected with line numbers. Blank lines are skipped.

The JSON report lists added/removed keys, changed top-level field names and counts. It does not include full records or changed-field values. Object member order is ignored; arrays retain their order. Parsed values are compared using JSON serialization, so `1` and `1.0` differ, as do `true` and `1`. JSON object members use the standard decoder's last-value behavior for repeated field names. Unicode separators inside strings do not start a new record.

Repeat `--ignore-field` to exclude volatile top-level fields from comparison. This does not suppress added/removed records or change the input files. Nested changes report their containing top-level field. Added keys follow right-file order; removed and changed keys follow left-file order.

`--output report.json` writes a new file and refuses to overwrite an existing one. Both snapshots are held in memory; there is no fuzzy matching, streaming, chain verification or schema inference. Use a key that is unique within each file.

Run `python -m unittest discover -s tests -v`. CI installs the package and runs the same offline tests on Python 3.12. Status: working local tool, with synthetic fixtures; suitable for inspecting saved snapshots.
