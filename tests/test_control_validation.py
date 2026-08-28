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
        "north_star_ref": "NORTH-STAR-REVIEW",
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
        "reviewed_at": None,
    }


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
        document["reviews"] = [_north_star_review()]
        _save(review_path, document)
        previous_root = Path(self.temporary.name) / "previous-assets"
        shutil.copytree(self.root, previous_root)
        document["reviews"][0]["alignment"] = "aligned"
        document["revision"] += 1
        _save(review_path, document)

        errors = self.validate(previous_root)

        self.assertTrue(any("immutable record 'NSR-001' was modified" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
