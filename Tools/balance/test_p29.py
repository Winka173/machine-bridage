"""Prompt 29 tests for the Python side (S01, S02, S09). Written in the cloud; run locally with
    python -m unittest Tools/balance/test_p29.py
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import p29_apply as A  # noqa: E402

ROOT = A.ROOT


class RoundHalfUp(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(A.round_half_up(12.5), 13)
        self.assertEqual(A.round_half_up(19.5), 20)
        self.assertEqual(A.round_half_up(2.5), 3)  # Python's round() gives 2
        self.assertEqual(A.round_half_up(2485, 10), 2490)
        self.assertEqual(A.round_half_up(2484.9, 10), 2480)


class Rules(unittest.TestCase):
    def test_review_reads_status_columns_only(self):
        self.assertFalse(A.review({"reason": 'Dòng "Xem lại" đợt 1 bị áp nhầm', "status": "FIX"}))
        self.assertTrue(A.review({"status": "Xem lại"}))

    def test_every_mapped_path_has_a_mapper(self):
        for path in ("units.ifv.hp", "units.ifv.cost", "units.ifv.outgoingDamageMult", "units.ifv.dropDelaySec",
                     "units.fighter_jet.flare.maxCharges", "units.fighter_jet.flare.rechargeSec"):
            A.mapper({"field_path": path, "entity_id": path.split(".")[1]})
        with self.assertRaises(A.Unmapped):
            A.mapper({"field_path": "units.ifv.somethingNew"})

    def test_dry_run_has_no_conflict(self):
        out = A.run(["*"], dry=True)
        self.assertFalse([b for b, v in out.items() if v == "CONFLICT"])


class TurnRateLabel(unittest.TestCase):
    def test_document_prints_degrees_under_degree_labels(self):
        """S09 (R9): the design document converts the code's radians before printing them under °/s."""
        text = open(os.path.join(ROOT, "Tools", "docs", "programme.py"), encoding="utf-8").read()
        self.assertIn("Xoay thân (°/s)", text)
        self.assertRegex(text, r"deg\(raw\.get\('TurnRate'")
        self.assertNotIn("rad/s", re.sub(r"#.*", "", text).replace("radian mỗi giây", ""))


if __name__ == "__main__":
    unittest.main()
