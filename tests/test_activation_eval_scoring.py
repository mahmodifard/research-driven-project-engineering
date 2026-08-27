from __future__ import annotations

import unittest
from pathlib import Path

from tools.score_activation_evals import load_mapping, score_results, validate_cases


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CASES = load_mapping(REPOSITORY_ROOT / "evals" / "activation-cases.yaml")


class ActivationEvalScoringTests(unittest.TestCase):
    def test_case_manifest_is_valid(self) -> None:
        self.assertEqual([], validate_cases(CASES))

    def test_expected_observations_pass(self) -> None:
        results = {"results": []}
        for case in CASES["cases"]:
            expected = case["expected"]
            results["results"].append({
                "case_id": case["id"],
                "activation": expected["activation"],
                "mode": expected["allowed_modes"][0] if expected["allowed_modes"] else None,
                "observed_behaviors": expected["required_behaviors"],
            })
        self.assertEqual([], score_results(CASES, results))

    def test_activation_regression_fails(self) -> None:
        results = {"results": []}
        for case in CASES["cases"]:
            expected = case["expected"]
            results["results"].append({
                "case_id": case["id"],
                "activation": expected["activation"],
                "mode": expected["allowed_modes"][0] if expected["allowed_modes"] else None,
                "observed_behaviors": expected["required_behaviors"],
            })
        results["results"][0]["activation"] = False

        errors = score_results(CASES, results)

        self.assertTrue(any("activation mismatch" in error for error in errors), errors)

    def test_unknown_result_case_fails(self) -> None:
        errors = score_results(CASES, {"results": [{
            "case_id": "ACT-UNKNOWN-001",
            "activation": False,
            "mode": None,
            "observed_behaviors": [],
        }]})

        self.assertTrue(any("unknown case" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
