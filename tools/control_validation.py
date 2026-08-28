"""Semantic validation for machine-readable project-control YAML."""

from __future__ import annotations

import re
from copy import deepcopy
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

    if previous_root is not None:
        previous_documents = _load_documents(previous_root, errors)
        _validate_history(documents, previous_documents, vocabulary, errors)
    return errors
