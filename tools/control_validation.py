"""Semantic validation for machine-readable project-control YAML."""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import yaml


ARABIC_SCRIPT = re.compile(r"[\u0600-\u06ff]")
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED_ENVELOPE = {
    "schema_version",
    "document_type",
    "document_id",
    "revision",
    "language",
    "machine_readable",
    "status",
    "created_at",
    "updated_at",
    "owners",
    "source_refs",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def load_yaml(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def _walk(value: Any, location: str = "") -> Iterable[tuple[str, Any]]:
    yield location, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}" if location else str(key)
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{location}[{index}]")


def _get_path(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _semantic_document(value: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(value)
    result.pop("revision", None)
    result.pop("updated_at", None)
    return result


def _record_entries(
    document: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[tuple[str, str, dict[str, Any]]]:
    document_type = document.get("document_type")
    artifact_contract = vocabulary.get("artifact_contracts", {}).get(document_type, {})
    entries: list[tuple[str, str, dict[str, Any]]] = []
    for collection_path, record_type in artifact_contract.get("collections", {}).items():
        records = _get_path(document, collection_path)
        if records is None:
            continue
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if isinstance(record, dict):
                entries.append((record_type, f"{collection_path}[{index}]", record))
    return entries


def _all_identifiers(
    documents: dict[Path, dict[str, Any]],
    errors: list[str],
) -> set[str]:
    identifiers: dict[str, str] = {}
    for path, document in documents.items():
        document_id = document.get("document_id")
        if isinstance(document_id, str) and document_id:
            location = f"{path}:document_id"
            if document_id in identifiers:
                errors.append(f"{location}: duplicate identifier {document_id!r}; first seen at {identifiers[document_id]}")
            else:
                identifiers[document_id] = location
        for location, value in _walk(document):
            if not isinstance(value, dict) or "id" not in value:
                continue
            record_id = value.get("id")
            if not isinstance(record_id, str) or not record_id:
                errors.append(f"{path}:{location}.id: record id must be a non-empty string")
                continue
            record_location = f"{path}:{location}.id"
            if record_id in identifiers:
                errors.append(f"{record_location}: duplicate identifier {record_id!r}; first seen at {identifiers[record_id]}")
            else:
                identifiers[record_id] = record_location
    return set(identifiers)


def _validate_document(
    path: Path,
    document: dict[str, Any],
    vocabulary: dict[str, Any],
    errors: list[str],
) -> None:
    missing = sorted(REQUIRED_ENVELOPE - document.keys())
    if missing:
        errors.append(f"{path}: missing envelope fields: {', '.join(missing)}")
    if document.get("language") != "en":
        errors.append(f"{path}: language must be 'en'")
    if document.get("machine_readable") is not True:
        errors.append(f"{path}: machine_readable must be true")
    revision = document.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(f"{path}: revision must be a positive integer")

    document_statuses = vocabulary.get("enums", {}).get("document_status", [])
    if document.get("status") not in document_statuses:
        errors.append(f"{path}: invalid document status {document.get('status')!r}")

    for location, value in _walk(document):
        if not isinstance(value, dict):
            continue
        for key in value:
            schema_path_key = document.get("document_type") == "control_vocabulary" and isinstance(key, str) and all(
                SNAKE_CASE.fullmatch(part) for part in key.split(".")
            )
            if (not isinstance(key, str) or not SNAKE_CASE.fullmatch(key)) and not schema_path_key:
                errors.append(f"{path}:{location or '<root>'}: non-snake-case key {key!r}")

    document_type = document.get("document_type")
    enum_fields = vocabulary.get("document_enum_fields", {}).get(document_type, {})
    enums = vocabulary.get("enums", {})
    for field_path, enum_name in enum_fields.items():
        value = _get_path(document, field_path)
        if value not in enums.get(enum_name, []):
            errors.append(f"{path}:{field_path}: invalid {enum_name} value {value!r}")


def _validate_records(
    path: Path,
    document: dict[str, Any],
    vocabulary: dict[str, Any],
    errors: list[str],
) -> None:
    contracts = vocabulary.get("record_contracts", {})
    prefixes = vocabulary.get("id_prefixes", {})
    enums = vocabulary.get("enums", {})
    artifact_contract = vocabulary.get("artifact_contracts", {}).get(document.get("document_type"), {})
    for collection_path, record_type in artifact_contract.get("collections", {}).items():
        records = _get_path(document, collection_path)
        if records is not None and not isinstance(records, list):
            errors.append(f"{path}:{collection_path}: contracted collection must be a list")
        elif isinstance(records, list):
            for index, record in enumerate(records):
                if not isinstance(record, dict):
                    errors.append(f"{path}:{collection_path}[{index}]: {record_type} record must be a mapping")

    for record_type, location, record in _record_entries(document, vocabulary):
        contract = contracts.get(record_type)
        if not isinstance(contract, dict):
            errors.append(f"{path}:{location}: unknown record contract {record_type!r}")
            continue
        missing = [field for field in contract.get("required_fields", []) if field not in record]
        if missing:
            errors.append(f"{path}:{location}: missing {record_type} fields: {', '.join(missing)}")
        prefix_name = contract.get("id_prefix")
        expected_prefix = prefixes.get(prefix_name)
        record_id = record.get("id")
        if expected_prefix and (not isinstance(record_id, str) or not record_id.startswith(expected_prefix)):
            errors.append(f"{path}:{location}.id: expected prefix {expected_prefix!r}, got {record_id!r}")
        for field, enum_name in contract.get("enum_fields", {}).items():
            value = record.get(field)
            if field in record and value not in enums.get(enum_name, []):
                errors.append(f"{path}:{location}.{field}: invalid {enum_name} value {value!r}")
        for field, expected_value in contract.get("constant_fields", {}).items():
            if field in record and record.get(field) != expected_value:
                errors.append(
                    f"{path}:{location}.{field}: expected constant {expected_value!r}, got {record.get(field)!r}"
                )
        for field in contract.get("non_null_fields", []):
            if field in record and record.get(field) is None:
                errors.append(f"{path}:{location}.{field}: value must not be null")


def _parse_utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed if parsed.utcoffset() is not None else None


def _validate_north_star_constitution(
    documents: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    for path, document in documents.items():
        if document.get("document_type") != "north_star_review":
            continue

        raw_versions = document.get("north_star_versions", [])
        raw_events = document.get("north_star_events", [])
        raw_reviews = document.get("reviews", [])
        raw_bindings = document.get("review_bindings", [])
        versions = [value for value in raw_versions if isinstance(value, dict)] if isinstance(raw_versions, list) else []
        events = [value for value in raw_events if isinstance(value, dict)] if isinstance(raw_events, list) else []
        reviews = [value for value in raw_reviews if isinstance(value, dict)] if isinstance(raw_reviews, list) else []
        bindings = [value for value in raw_bindings if isinstance(value, dict)] if isinstance(raw_bindings, list) else []

        version_by_id: dict[str, dict[str, Any]] = {}
        version_numbers: list[int] = []
        effective_at_by_id: dict[str, datetime] = {}
        for index, version in enumerate(versions):
            location = f"{path}:north_star_versions[{index}]"
            version_id = version.get("id")
            if isinstance(version_id, str) and version_id:
                version_by_id[version_id] = version

            version_number = version.get("version")
            if not isinstance(version_number, int) or isinstance(version_number, bool) or version_number < 1:
                errors.append(f"{location}.version: value must be a positive integer")
            else:
                version_numbers.append(version_number)

            objective = version.get("objective")
            if not isinstance(objective, str) or not objective.strip():
                errors.append(f"{location}.objective: value must be a non-empty string")
            for field in ("target_user_refs", "outcome_metric_refs"):
                value = version.get(field)
                if not isinstance(value, list) or not value:
                    errors.append(f"{location}.{field}: value must be a non-empty list")
            for field in ("invariant_refs", "non_goal_refs", "evidence_refs", "decision_refs", "source_refs"):
                if not isinstance(version.get(field), list):
                    errors.append(f"{location}.{field}: value must be a list")

            provenance = []
            for field in ("evidence_refs", "decision_refs", "source_refs"):
                value = version.get(field)
                if isinstance(value, list):
                    provenance.extend(item for item in value if isinstance(item, str) and item.strip())
            if not provenance:
                errors.append(f"{location}: at least one evidence, decision, or source reference is required")

            for field in ("approved_by_ref", "change_reason"):
                value = version.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{location}.{field}: value must be a non-empty string")

            timestamps: dict[str, datetime] = {}
            for field in ("created_at", "approved_at", "effective_at"):
                parsed = _parse_utc_timestamp(version.get(field))
                if parsed is None:
                    errors.append(f"{location}.{field}: value must be an ISO 8601 UTC timestamp")
                else:
                    timestamps[field] = parsed
            if set(timestamps) == {"created_at", "approved_at", "effective_at"}:
                if timestamps["created_at"] > timestamps["approved_at"]:
                    errors.append(f"{location}: created_at must not be later than approved_at")
                if timestamps["approved_at"] > timestamps["effective_at"]:
                    errors.append(f"{location}: approved_at must not be later than effective_at")
            if isinstance(version_id, str) and "effective_at" in timestamps:
                effective_at_by_id[version_id] = timestamps["effective_at"]

        if version_numbers:
            expected_numbers = list(range(1, len(version_numbers) + 1))
            if version_numbers != expected_numbers:
                errors.append(
                    f"{path}:north_star_versions: versions must be ordered and contiguous from 1; got {version_numbers!r}"
                )

        ordered_versions = sorted(
            (value for value in versions if isinstance(value.get("version"), int) and not isinstance(value.get("version"), bool)),
            key=lambda value: value["version"],
        )
        for index, version in enumerate(ordered_versions):
            location = f"{path}:north_star_versions[{index}]"
            expected_previous = None if index == 0 else ordered_versions[index - 1].get("id")
            if version.get("supersedes_ref") != expected_previous:
                errors.append(
                    f"{location}.supersedes_ref: expected {expected_previous!r}, got {version.get('supersedes_ref')!r}"
                )
            if index > 0:
                previous_id = ordered_versions[index - 1].get("id")
                current_id = version.get("id")
                previous_time = effective_at_by_id.get(previous_id)
                current_time = effective_at_by_id.get(current_id)
                if previous_time is not None and current_time is not None and current_time <= previous_time:
                    errors.append(f"{location}.effective_at: value must be later than the superseded version")

        events_by_version: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        event_version_order: list[str] = []
        for index, event in enumerate(events):
            location = f"{path}:north_star_events[{index}]"
            version_ref = event.get("north_star_version_ref")
            if not isinstance(version_ref, str) or version_ref not in version_by_id:
                errors.append(f"{location}.north_star_version_ref: unknown North Star version {version_ref!r}")
                continue
            events_by_version.setdefault(version_ref, []).append((index, event))
            event_version_order.append(version_ref)
            if _parse_utc_timestamp(event.get("occurred_at")) is None:
                errors.append(f"{location}.occurred_at: value must be an ISO 8601 UTC timestamp")
            for field in ("authorized_by_ref", "reason"):
                value = event.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{location}.{field}: value must be a non-empty string")

        expected_version_order = [value.get("id") for value in ordered_versions if isinstance(value.get("id"), str)]
        if event_version_order and event_version_order != expected_version_order:
            errors.append(
                f"{path}:north_star_events: events must follow version order {expected_version_order!r}; got {event_version_order!r}"
            )

        for index, version in enumerate(ordered_versions):
            version_id = version.get("id")
            matching_events = events_by_version.get(version_id, [])
            if len(matching_events) != 1:
                errors.append(
                    f"{path}:north_star_versions[{index}]: version {version_id!r} must have exactly one activation event"
                )
                continue
            event_index, event = matching_events[0]
            location = f"{path}:north_star_events[{event_index}]"
            expected_type = "activation" if index == 0 else "supersession"
            expected_previous = None if index == 0 else ordered_versions[index - 1].get("id")
            if event.get("event_type") != expected_type:
                errors.append(f"{location}.event_type: expected {expected_type!r}")
            if event.get("previous_active_version_ref") != expected_previous:
                errors.append(
                    f"{location}.previous_active_version_ref: expected {expected_previous!r}, got {event.get('previous_active_version_ref')!r}"
                )
            if event.get("occurred_at") != version.get("effective_at"):
                errors.append(f"{location}.occurred_at: value must equal the version effective_at")

        next_effective_by_id: dict[str, datetime] = {}
        for index, version in enumerate(ordered_versions[:-1]):
            current_id = version.get("id")
            next_id = ordered_versions[index + 1].get("id")
            if isinstance(current_id, str) and next_id in effective_at_by_id:
                next_effective_by_id[current_id] = effective_at_by_id[next_id]

        review_by_id = {
            review.get("id"): review
            for review in reviews
            if isinstance(review.get("id"), str) and review.get("id")
        }
        bindings_by_review: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for index, binding in enumerate(bindings):
            location = f"{path}:review_bindings[{index}]"
            review_ref = binding.get("review_ref")
            version_ref = binding.get("north_star_version_ref")
            if not isinstance(review_ref, str) or review_ref not in review_by_id:
                errors.append(f"{location}.review_ref: unknown North Star review {review_ref!r}")
            else:
                bindings_by_review.setdefault(review_ref, []).append((index, binding))
            if not isinstance(version_ref, str) or version_ref not in version_by_id:
                errors.append(f"{location}.north_star_version_ref: unknown North Star version {version_ref!r}")
            if _parse_utc_timestamp(binding.get("bound_at")) is None:
                errors.append(f"{location}.bound_at: value must be an ISO 8601 UTC timestamp")
            limitations = binding.get("limitations")
            if not isinstance(limitations, list) or not limitations:
                errors.append(f"{location}.limitations: legacy migration limitations must be a non-empty list")
            provenance = []
            for field in ("evidence_refs", "source_refs"):
                value = binding.get(field)
                if isinstance(value, list):
                    provenance.extend(item for item in value if isinstance(item, str) and item.strip())
            if not provenance:
                errors.append(f"{location}: at least one evidence or source reference is required")

        for index, review in enumerate(reviews):
            location = f"{path}:reviews[{index}]"
            version_ref = review.get("north_star_version_ref")
            review_id = review.get("id")
            matching_bindings = bindings_by_review.get(review_id, []) if isinstance(review_id, str) else []
            if version_ref is None:
                if review.get("north_star_ref") != "NORTH-STAR-REVIEW":
                    errors.append(f"{location}: review must pin north_star_version_ref")
                    continue
                if len(matching_bindings) != 1:
                    errors.append(
                        f"{location}: legacy review {review_id!r} must have exactly one immutable migration binding"
                    )
                    continue
                version_ref = matching_bindings[0][1].get("north_star_version_ref")
            elif matching_bindings:
                errors.append(f"{location}: directly versioned review must not have a legacy migration binding")
            if not isinstance(version_ref, str) or version_ref not in version_by_id:
                errors.append(f"{location}.north_star_version_ref: unknown North Star version {version_ref!r}")
                continue
            reviewed_at = _parse_utc_timestamp(review.get("reviewed_at"))
            if reviewed_at is None:
                errors.append(f"{location}.reviewed_at: value must be an ISO 8601 UTC timestamp")
                continue
            effective_at = effective_at_by_id.get(version_ref)
            next_effective_at = next_effective_by_id.get(version_ref)
            if effective_at is not None and reviewed_at < effective_at:
                errors.append(f"{location}: review predates North Star version {version_ref!r}")
            if next_effective_at is not None and reviewed_at >= next_effective_at:
                errors.append(f"{location}: North Star version {version_ref!r} was no longer effective at review time")


def _validate_references(
    documents: dict[Path, dict[str, Any]],
    vocabulary: dict[str, Any],
    identifiers: set[str],
    errors: list[str],
) -> None:
    controlled_prefixes = tuple(vocabulary.get("id_prefixes", {}).values())
    for path, document in documents.items():
        for location, value in _walk(document):
            if not isinstance(value, dict):
                continue
            for key, candidate in value.items():
                if key == "source_refs" or not (key.endswith("_ref") or key.endswith("_refs")):
                    continue
                candidates = candidate if isinstance(candidate, list) else [candidate]
                for reference in candidates:
                    if not isinstance(reference, str) or not reference.startswith(controlled_prefixes):
                        continue
                    if reference not in identifiers:
                        errors.append(f"{path}:{location or '<root>'}.{key}: dangling reference {reference!r}")


def _index_contracted_records(
    documents: dict[Path, dict[str, Any]],
    vocabulary: dict[str, Any],
) -> dict[tuple[Path, str, str], tuple[str, dict[str, Any]]]:
    result: dict[tuple[Path, str, str], tuple[str, dict[str, Any]]] = {}
    for path, document in documents.items():
        for record_type, location, record in _record_entries(document, vocabulary):
            record_id = record.get("id")
            if isinstance(record_id, str):
                result[(path, record_type, record_id)] = (location, record)
    return result


def _validate_history(
    current: dict[Path, dict[str, Any]],
    previous: dict[Path, dict[str, Any]],
    vocabulary: dict[str, Any],
    errors: list[str],
) -> None:
    for path, previous_document in previous.items():
        current_document = current.get(path)
        if current_document is None:
            errors.append(f"{path}: previous canonical document was removed; retire or supersede it explicitly")
            continue
        if _semantic_document(previous_document) != _semantic_document(current_document):
            previous_revision = previous_document.get("revision")
            current_revision = current_document.get("revision")
            if not isinstance(current_revision, int) or not isinstance(previous_revision, int) or current_revision <= previous_revision:
                errors.append(f"{path}: semantic change requires revision greater than {previous_revision!r}")

    previous_records = _index_contracted_records(previous, vocabulary)
    current_records = _index_contracted_records(current, vocabulary)
    contracts = vocabulary.get("record_contracts", {})
    transitions = vocabulary.get("state_transitions", {}).get("workflow_state", {})
    for key, (previous_location, previous_record) in previous_records.items():
        path, record_type, record_id = key
        contract = contracts.get(record_type, {})
        current_entry = current_records.get(key)
        if current_entry is None:
            if contract.get("immutable_after_append"):
                errors.append(f"{path}:{previous_location}: immutable record {record_id!r} was removed")
            continue
        current_location, current_record = current_entry
        if contract.get("immutable_after_append") and current_record != previous_record:
            errors.append(f"{path}:{current_location}: immutable record {record_id!r} was modified")
        for field in contract.get("append_only_fields", []):
            old_value = previous_record.get(field, [])
            new_value = current_record.get(field, [])
            if not isinstance(old_value, list) or not isinstance(new_value, list) or new_value[: len(old_value)] != old_value:
                errors.append(f"{path}:{current_location}.{field}: append-only history was rewritten")
        if record_type == "task":
            old_state = previous_record.get("workflow_state")
            new_state = current_record.get("workflow_state")
            if old_state != new_state and new_state not in transitions.get(old_state, []):
                errors.append(f"{path}:{current_location}.workflow_state: illegal transition {old_state!r} -> {new_state!r}")


def _load_documents(root: Path, errors: list[str]) -> dict[Path, dict[str, Any]]:
    documents: dict[Path, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.yaml")):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if "\t" in text:
            errors.append(f"{relative}: tab character found")
        if ARABIC_SCRIPT.search(text):
            errors.append(f"{relative}: canonical controls must be English-only")
        try:
            value = load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{relative}: top-level YAML value must be a mapping")
            continue
        documents[relative] = value
    return documents


def validate_control_directory(
    root: Path,
    vocabulary_path: Path,
    previous_root: Path | None = None,
) -> list[str]:
    """Return semantic contract violations for a control directory."""

    errors: list[str] = []
    if not vocabulary_path.is_file():
        return [f"control vocabulary is missing: {vocabulary_path}"]
    try:
        vocabulary = load_yaml(vocabulary_path)
    except yaml.YAMLError as exc:
        return [f"control vocabulary is invalid: {exc}"]
    if not isinstance(vocabulary, dict):
        return ["control vocabulary must be a mapping"]

    documents = _load_documents(root, errors)
    if not documents:
        errors.append(f"no canonical YAML controls found under {root}")
        return errors
    for path, document in documents.items():
        _validate_document(path, document, vocabulary, errors)
        _validate_records(path, document, vocabulary, errors)
    identifiers = _all_identifiers(documents, errors)
    _validate_references(documents, vocabulary, identifiers, errors)
    _validate_north_star_constitution(documents, errors)

    if previous_root is not None:
        previous_documents = _load_documents(previous_root, errors)
        _validate_history(documents, previous_documents, vocabulary, errors)
    return errors
