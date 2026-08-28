from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.control_validation import validate_control_directory


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _save(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _task(state: str = "planned") -> dict:
    return {
        "id": "TSK-001",
        "title": "Validate the contract",
        "requirement_refs": [],
        "acceptance_refs": [],
        "slice_ref": None,
        "dependency_refs": [],
        "workflow_state": state,
        "owner_ref": None,
        "scope": [],
        "validation_refs": [],
        "risk_refs": [],
        "status_transition_refs": [],
    }


def _north_star_review() -> dict:
    return {
        "id": "NSR-001",
        "checkpoint_kind": "architecture",
        "checkpoint_ref": None,
        "baseline_ref": None,
        "north_star_version_ref": "NSV-001",
        "reviewer_session_ref": None,
        "reviewer_role": "north_star_reviewer",
        "reviewer_mode": "local_self_check",
        "alignment": "unknown",
        "product_value": "unproven",
        "consumability": "unknown",
        "integration_risk": "unknown",
        "adoption_friction": "unknown",
        "evidence_refs": [],
        "findings": [],
        "challenges": [],
        "evidence_required": [],
        "recommendation": "validate",
        "blocking_authority": False,
        "reviewed_at": "2026-08-01T12:00:00Z",
    }


def _north_star_version(
    identifier: str = "NSV-001",
    version: int = 1,
    effective_at: str = "2026-08-01T00:00:00Z",
    supersedes_ref: str | None = None,
) -> dict:
    return {
        "id": identifier,
        "version": version,
        "objective": "Deliver a consumable product outcome",
        "target_user_refs": ["USER-primary"],
        "outcome_metric_refs": ["METRIC-adoption"],
        "invariant_refs": [],
        "non_goal_refs": [],
        "evidence_refs": [],
        "decision_refs": [],
        "approved_by_ref": "AUTH-product-owner",
        "approved_at": effective_at,
        "effective_at": effective_at,
        "supersedes_ref": supersedes_ref,
        "change_reason": "Initial approved North Star" if version == 1 else "Approved product-direction change",
        "created_at": effective_at,
        "source_refs": ["user-approved-product-brief"],
    }


def _north_star_event(
    identifier: str = "NSE-001",
    version_ref: str = "NSV-001",
    event_type: str = "activation",
    occurred_at: str = "2026-08-01T00:00:00Z",
    previous_active_version_ref: str | None = None,
) -> dict:
    return {
        "id": identifier,
        "event_type": event_type,
        "north_star_version_ref": version_ref,
        "previous_active_version_ref": previous_active_version_ref,
        "authorized_by_ref": "AUTH-product-owner",
        "reason": "Activate the approved North Star version",
        "occurred_at": occurred_at,
        "evidence_refs": [],
        "source_refs": ["user-approval-record"],
    }


def _legacy_north_star_review() -> dict:
    review = _north_star_review()
    review.pop("north_star_version_ref")
    review["north_star_ref"] = "NORTH-STAR-REVIEW"
    return review


def _legacy_review_binding() -> dict:
    return {
        "id": "NSB-001",
        "binding_kind": "legacy_migration",
        "review_ref": "NSR-001",
        "north_star_version_ref": "NSV-001",
        "bound_by_ref": "AUTH-product-owner",
        "bound_at": "2026-08-03T00:00:00Z",
        "evidence_refs": [],
        "limitations": ["The original 0.3 review did not pin a constitution version"],
        "source_refs": ["migration-audit-record"],
    }


def _set_north_star(document: dict, versions: list[dict] | None = None, events: list[dict] | None = None) -> None:
    document["north_star_versions"] = versions or [_north_star_version()]
    document["north_star_events"] = events or [_north_star_event()]


class ControlValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "assets"
        shutil.copytree(REPOSITORY_ROOT / "assets", self.root)
        self.vocabulary = self.root / "project-docs" / "control-vocabulary.yaml"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validate(self, previous_root: Path | None = None) -> list[str]:
        return validate_control_directory(self.root, self.vocabulary, previous_root)

    def test_canonical_templates_pass_semantic_validation(self) -> None:
        self.assertEqual([], self.validate())

    def test_required_record_fields_are_enforced(self) -> None:
        roadmap_path = self.root / "project-docs" / "roadmap.yaml"
        roadmap = _load(roadmap_path)
        roadmap["gates"] = [{"id": "GATE-001"}]
        _save(roadmap_path, roadmap)

        errors = self.validate()

        self.assertTrue(any("missing gate fields" in error for error in errors), errors)

    def test_contracted_collection_rejects_non_mapping_records(self) -> None:
        roadmap_path = self.root / "project-docs" / "roadmap.yaml"
        roadmap = _load(roadmap_path)
        roadmap["gates"] = ["GATE-001"]
        _save(roadmap_path, roadmap)

        errors = self.validate()

        self.assertTrue(any("gate record must be a mapping" in error for error in errors), errors)

    def test_enum_and_id_prefix_are_enforced(self) -> None:
        tracker_path = self.root / "project-docs" / "implementation-tracker.yaml"
        tracker = _load(tracker_path)
        task = _task("almost_done")
        task["id"] = "BAD-001"
        tracker["tasks"] = [task]
        _save(tracker_path, tracker)

        errors = self.validate()

        self.assertTrue(any("expected prefix 'TSK-'" in error for error in errors), errors)
        self.assertTrue(any("invalid workflow_state" in error for error in errors), errors)

    def test_duplicate_ids_and_dangling_refs_are_rejected(self) -> None:
        spec_path = self.root / "project-docs" / "product-spec.yaml"
        spec = _load(spec_path)
        spec["requirements"] = [{"id": "REQ-001"}]
        spec["acceptance_criteria"] = [{"id": "REQ-001"}]
        _save(spec_path, spec)
        tracker_path = self.root / "project-docs" / "implementation-tracker.yaml"
        tracker = _load(tracker_path)
        task = _task()
        task["requirement_refs"] = ["REQ-404"]
        tracker["tasks"] = [task]
        _save(tracker_path, tracker)

        errors = self.validate()

        self.assertTrue(any("duplicate identifier 'REQ-001'" in error for error in errors), errors)
        self.assertTrue(any("dangling reference 'REQ-404'" in error for error in errors), errors)

    def test_semantic_change_requires_revision_increment(self) -> None:
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        roadmap_path = self.root / "project-docs" / "roadmap.yaml"
        roadmap = _load(roadmap_path)
        roadmap["non_goal_refs"] = ["REQ-001"]
        _save(roadmap_path, roadmap)

        errors = self.validate(previous_root)

        self.assertTrue(any("semantic change requires revision" in error for error in errors), errors)

    def test_illegal_task_transition_is_rejected(self) -> None:
        tracker_path = self.root / "project-docs" / "implementation-tracker.yaml"
        tracker = _load(tracker_path)
        tracker["tasks"] = [_task("planned")]
        _save(tracker_path, tracker)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        tracker["tasks"][0]["workflow_state"] = "implemented"
        tracker["revision"] += 1
        _save(tracker_path, tracker)

        errors = self.validate(previous_root)

        self.assertTrue(any("illegal transition 'planned' -> 'implemented'" in error for error in errors), errors)

    def test_evidence_is_immutable_after_append(self) -> None:
        tracker_path = self.root / "project-docs" / "implementation-tracker.yaml"
        tracker = _load(tracker_path)
        tracker["evidence_records"] = [{
            "id": "EVD-001",
            "subject_refs": [],
            "lane": "automated_test",
            "result": "fail",
            "artifact_refs": [],
            "environment_refs": [],
            "action": "python -m unittest",
            "observed_at": "2026-08-27T00:00:00Z",
            "assertions": [],
            "limitations": [],
            "source_refs": [],
        }]
        _save(tracker_path, tracker)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        tracker["evidence_records"][0]["result"] = "pass"
        tracker["revision"] += 1
        _save(tracker_path, tracker)

        errors = self.validate(previous_root)

        self.assertTrue(any("immutable record 'EVD-001' was modified" in error for error in errors), errors)

    def test_north_star_reviewer_authority_is_enforced(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        review = _north_star_review()
        review["reviewer_role"] = "module_writer"
        review["blocking_authority"] = True
        document["reviews"] = [review]
        _save(review_path, document)

        errors = self.validate()

        self.assertTrue(any("reviewer_role: expected constant 'north_star_reviewer'" in error for error in errors), errors)
        self.assertTrue(any("blocking_authority: expected constant False" in error for error in errors), errors)

    def test_north_star_review_is_immutable_after_append(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        document["reviews"] = [_north_star_review()]
        _save(review_path, document)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        document["reviews"][0]["alignment"] = "aligned"
        document["revision"] += 1
        _save(review_path, document)

        errors = self.validate(previous_root)

        self.assertTrue(any("immutable record 'NSR-001' was modified" in error for error in errors), errors)

    def test_versioned_north_star_chain_passes(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        versions = [
            _north_star_version(),
            _north_star_version("NSV-002", 2, "2026-08-02T00:00:00Z", "NSV-001"),
        ]
        events = [
            _north_star_event(),
            _north_star_event(
                "NSE-002",
                "NSV-002",
                "supersession",
                "2026-08-02T00:00:00Z",
                "NSV-001",
            ),
        ]
        _set_north_star(document, versions, events)
        review = _north_star_review()
        review["north_star_version_ref"] = "NSV-002"
        review["reviewed_at"] = "2026-08-02T12:00:00Z"
        document["reviews"] = [review]
        _save(review_path, document)

        self.assertEqual([], self.validate())

    def test_north_star_chain_rejects_version_gap_and_wrong_parent(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        versions = [
            _north_star_version(),
            _north_star_version("NSV-003", 3, "2026-08-03T00:00:00Z", "NSV-999"),
        ]
        events = [
            _north_star_event(),
            _north_star_event(
                "NSE-003",
                "NSV-003",
                "supersession",
                "2026-08-03T00:00:00Z",
                "NSV-999",
            ),
        ]
        _set_north_star(document, versions, events)
        _save(review_path, document)

        errors = self.validate()

        self.assertTrue(any("versions must be ordered and contiguous" in error for error in errors), errors)
        self.assertTrue(any("supersedes_ref: expected 'NSV-001'" in error for error in errors), errors)

    def test_north_star_activation_event_is_required(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        document["north_star_versions"] = [_north_star_version()]
        document["north_star_events"] = []
        _save(review_path, document)

        errors = self.validate()

        self.assertTrue(any("must have exactly one activation event" in error for error in errors), errors)

    def test_review_rejects_superseded_north_star_version(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        versions = [
            _north_star_version(),
            _north_star_version("NSV-002", 2, "2026-08-02T00:00:00Z", "NSV-001"),
        ]
        events = [
            _north_star_event(),
            _north_star_event(
                "NSE-002",
                "NSV-002",
                "supersession",
                "2026-08-02T00:00:00Z",
                "NSV-001",
            ),
        ]
        _set_north_star(document, versions, events)
        review = _north_star_review()
        review["reviewed_at"] = "2026-08-02T12:00:00Z"
        document["reviews"] = [review]
        _save(review_path, document)

        errors = self.validate()

        self.assertTrue(any("was no longer effective at review time" in error for error in errors), errors)

    def test_north_star_version_is_immutable_after_append(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        _save(review_path, document)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        document["north_star_versions"][0]["objective"] = "Rewrite the product objective in place"
        document["revision"] += 1
        _save(review_path, document)

        errors = self.validate(previous_root)

        self.assertTrue(any("immutable record 'NSV-001' was modified" in error for error in errors), errors)

    def test_legacy_review_migrates_without_rewriting_history(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        document["reviews"] = [_legacy_north_star_review()]
        document["review_bindings"] = [_legacy_review_binding()]
        _save(review_path, document)

        self.assertEqual([], self.validate())

    def test_legacy_review_requires_immutable_migration_binding(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        document["reviews"] = [_legacy_north_star_review()]
        _save(review_path, document)

        errors = self.validate()

        self.assertTrue(any("must have exactly one immutable migration binding" in error for error in errors), errors)

    def test_legacy_review_binding_is_immutable_after_append(self) -> None:
        review_path = self.root / "project-docs" / "north-star-review.yaml"
        document = _load(review_path)
        _set_north_star(document)
        document["reviews"] = [_legacy_north_star_review()]
        document["review_bindings"] = [_legacy_review_binding()]
        _save(review_path, document)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        document["review_bindings"][0]["limitations"] = ["Rewrite migration limitations"]
        document["revision"] += 1
        _save(review_path, document)

        errors = self.validate(previous_root)

        self.assertTrue(any("immutable record 'NSB-001' was modified" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
