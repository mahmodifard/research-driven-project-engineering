#!/usr/bin/env python3
"""Validate activation cases and score provider-neutral observed results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


CATEGORIES = {"direct", "indirect", "incomplete", "negative", "edge"}
MODES = {"discovery", "planning", "delivery", "recovery"}
MUTATION_POLICIES = {
    "prohibited",
    "control_artifacts_only",
    "request_scoped",
    "permitted_within_user_authority",
}


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level value must be a mapping")
    return value


def validate_cases(suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    behaviors = suite.get("behavior_vocabulary")
    cases = suite.get("cases")
    if not isinstance(behaviors, dict) or not behaviors:
        errors.append("behavior_vocabulary must be a non-empty mapping")
        behaviors = {}
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]
    seen: set[str] = set()
    for index, case in enumerate(cases):
        location = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{location}: case must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{location}.id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"{location}.id duplicates {case_id!r}")
        else:
            seen.add(case_id)
        if case.get("category") not in CATEGORIES:
            errors.append(f"{location}.category is invalid")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{location}.prompt must be non-empty")
        expected = case.get("expected")
        if not isinstance(expected, dict) or not isinstance(expected.get("activation"), bool):
            errors.append(f"{location}.expected.activation must be boolean")
            continue
        allowed_modes = expected.get("allowed_modes")
        if not isinstance(allowed_modes, list) or any(mode not in MODES for mode in allowed_modes):
            errors.append(f"{location}.expected.allowed_modes contains an invalid mode")
        if expected.get("mutation_policy") not in MUTATION_POLICIES:
            errors.append(f"{location}.expected.mutation_policy is invalid")
        for field in ("required_behaviors", "prohibited_behaviors"):
            values = expected.get(field)
            if not isinstance(values, list):
                errors.append(f"{location}.expected.{field} must be a list")
                continue
            unknown = sorted(set(values) - set(behaviors))
            if unknown:
                errors.append(f"{location}.expected.{field} has unknown behaviors: {', '.join(unknown)}")
    return errors


def score_results(suite: dict[str, Any], result_set: dict[str, Any]) -> list[str]:
    errors = validate_cases(suite)
    if errors:
        return errors
    results = result_set.get("results")
    if not isinstance(results, list):
        return ["results must be a list"]
    result_by_id: dict[str, dict[str, Any]] = {}
    for index, result in enumerate(results):
        if not isinstance(result, dict) or not isinstance(result.get("case_id"), str):
            errors.append(f"results[{index}] must contain case_id")
            continue
        case_id = result["case_id"]
        if case_id in result_by_id:
            errors.append(f"duplicate result for {case_id!r}")
        result_by_id[case_id] = result
    known_case_ids = {case["id"] for case in suite["cases"]}
    for unknown_case_id in sorted(set(result_by_id) - known_case_ids):
        errors.append(f"result references unknown case {unknown_case_id!r}")
    for case in suite["cases"]:
        case_id = case["id"]
        expected = case["expected"]
        observed = result_by_id.get(case_id)
        if observed is None:
            errors.append(f"missing result for {case_id!r}")
            continue
        if observed.get("activation") is not expected["activation"]:
            errors.append(f"{case_id}: activation mismatch")
        mode = observed.get("mode")
        if expected["activation"] and mode not in expected["allowed_modes"]:
            errors.append(f"{case_id}: mode {mode!r} is outside allowed modes")
        observed_behaviors = observed.get("observed_behaviors", [])
        if not isinstance(observed_behaviors, list):
            errors.append(f"{case_id}: observed_behaviors must be a list")
            continue
        missing = sorted(set(expected["required_behaviors"]) - set(observed_behaviors))
        prohibited = sorted(set(expected["prohibited_behaviors"]) & set(observed_behaviors))
        if missing:
            errors.append(f"{case_id}: missing required behaviors: {', '.join(missing)}")
        if prohibited:
            errors.append(f"{case_id}: observed prohibited behaviors: {', '.join(prohibited)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases")
    parser.add_argument("--results")
    args = parser.parse_args()
    try:
        suite = load_mapping(Path(args.cases))
        errors = score_results(suite, load_mapping(Path(args.results))) if args.results else validate_cases(suite)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors = [str(exc)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Activation eval validation passed" if not args.results else "Activation eval results passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
