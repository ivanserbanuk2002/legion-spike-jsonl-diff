import unittest

from jsonl_diff.compare import compare_records, parse_records


class SnapshotTests(unittest.TestCase):
    def test_reports_added_removed_and_changed_fields(self):
        before = parse_records('{"id":"a","state":"pending"}\n{"id":"b"}')
        after = parse_records('{"id":"a","state":"done"}\n{"id":"c"}')
        self.assertEqual(compare_records(before, after), {
            "added": ["c"], "removed": ["b"],
            "changed": [{"key": "a", "fields": ["state"]}],
            "counts": {"added": 1, "removed": 1, "changed": 1, "unchanged": 0},
        })

    def test_object_order_does_not_change_a_record(self):
        before = parse_records('{"id":"a","meta":{"x":1,"y":2}}')
        after = parse_records('{"meta":{"y":2,"x":1},"id":"a"}')
        self.assertEqual(compare_records(before, after)["counts"]["unchanged"], 1)

    def test_missing_field_differs_from_explicit_null(self):
        before = parse_records('{"id":"a"}')
        after = parse_records('{"id":"a","value":null}')
        self.assertEqual(compare_records(before, after)["changed"], [{"key": "a", "fields": ["value"]}])

    def test_boolean_and_number_are_different_inside_nested_values(self):
        before = parse_records('{"id":"a","meta":[true]}')
        after = parse_records('{"id":"a","meta":[1]}')
        self.assertEqual(compare_records(before, after)["counts"]["changed"], 1)

    def test_ignores_named_fields_without_mutating_inputs(self):
        before = parse_records('{"id":"a","observed":1}')
        after = parse_records('{"id":"a","observed":2}')
        self.assertEqual(compare_records(before, after, ["observed"])["changed"], [])
        self.assertEqual(after["a"]["observed"], 2)

    def test_blank_lines_and_custom_identifier(self):
        self.assertEqual(list(parse_records('\n{"eventId":"x"}\n\n', "eventId")), ["x"])
        self.assertEqual(compare_records({}, {})["counts"]["unchanged"], 0)

    def test_rejects_ambiguous_or_missing_keys_with_line_numbers(self):
        inputs = ['{"id":"x"}\n{"id":"x"}', '\n{"value":1}', '\n{"id":" "}', '\n{"id":1}', '\n[]']
        for text in inputs:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "line 2"):
                parse_records(text)

    def test_rejects_nonfinite_numbers_in_nested_data(self):
        for number in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, "line 1"):
                parse_records('{"id":"a","meta":[' + number + ']}')

    def test_rejects_bad_json_and_invalid_key_option(self):
        with self.assertRaisesRegex(ValueError, "line 1"):
            parse_records('{"id":')
        with self.assertRaises(ValueError):
            parse_records("", " ")

    def test_unicode_separators_inside_json_strings_are_not_record_boundaries(self):
        for separator in ("\u2028", "\u0085"):
            with self.subTest(separator=repr(separator)):
                row = '{"id":"a","text":"before' + separator + 'after"}'
                self.assertEqual(parse_records(row)["a"]["text"], "before" + separator + "after")


if __name__ == "__main__":
    unittest.main()
