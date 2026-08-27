#!/usr/bin/env python3
"""Validate the public Agent Skill package and canonical control templates."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ARABIC_SCRIPT = re.compile(r"[\u0600-\u06ff]")
FRONTMATTER = re.compile(r"^---\n(?P<body>.*?)\n---", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\]\((?P<target>[^)]+)\)")
SKILL_NAME = "research-driven-project-engineering"
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
SENSITIVE_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[opsu]_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "windows_user_path": re.compile(r"(?i)\bC:\\Users\\[^\\\s]+"),
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
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


def validate_skill_frontmatter(root: Path, errors: list[str]) -> None:
    path = root / "SKILL.md"
    if not path.is_file():
        errors.append("SKILL.md is missing")
        return
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = FRONTMATTER.match(text)
    if not match:
        errors.append("SKILL.md frontmatter is missing or malformed")
        return
    try:
        metadata = yaml.safe_load(match.group("body"))
    except yaml.YAMLError as exc:
        errors.append(f"SKILL.md frontmatter YAML error: {exc}")
        return
    if not isinstance(metadata, dict):
        errors.append("SKILL.md frontmatter must be a mapping")
        return
    if metadata.get("name") != SKILL_NAME:
        errors.append(f"SKILL.md name must be {SKILL_NAME!r}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md requires a non-empty description")
    elif len(description) > 1024:
        errors.append("SKILL.md description exceeds 1024 characters")


def validate_public_package(root: Path, errors: list[str]) -> None:
    for required in ("README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md"):
        if not (root / required).is_file():
            errors.append(f"public package file is missing: {required}")
    license_path = root / "LICENSE"
    if license_path.is_file() and not license_path.read_text(encoding="utf-8").startswith("MIT License"):
        errors.append("LICENSE must contain the approved MIT license")


def validate_agent_metadata(root: Path, errors: list[str]) -> None:
    path = root / "agents" / "openai.yaml"
    if not path.is_file():
        errors.append("agents/openai.yaml is missing")
        return
    try:
        data = load_yaml(path)
    except yaml.YAMLError as exc:
        errors.append(f"{path.relative_to(root)}: {exc}")
        return
    prompt = data.get("interface", {}).get("default_prompt") if isinstance(data, dict) else None
    if not isinstance(prompt, str) or f"${SKILL_NAME}" not in prompt:
        errors.append("agents/openai.yaml default_prompt must explicitly name the skill")


def validate_canonical_assets(root: Path, errors: list[str]) -> None:
    assets_root = root / "assets"
    yaml_files = sorted(assets_root.rglob("*.yaml"))
    if not yaml_files:
        errors.append("no canonical YAML assets found")
        return
    non_yaml = [path for path in assets_root.rglob("*") if path.is_file() and path.suffix != ".yaml"]
    for path in non_yaml:
        errors.append(f"canonical asset must be YAML: {path.relative_to(root)}")
    for path in yaml_files:
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if "\t" in text:
            errors.append(f"{relative}: tab character found")
        if ARABIC_SCRIPT.search(text):
            errors.append(f"{relative}: canonical assets must be English-only")
        try:
            data = load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{relative}: top-level YAML value must be a mapping")
            continue
        missing = sorted(REQUIRED_ENVELOPE - data.keys())
        if missing:
            errors.append(f"{relative}: missing envelope fields: {', '.join(missing)}")
        if data.get("language") != "en":
            errors.append(f"{relative}: language must be 'en'")
        if data.get("machine_readable") is not True:
            errors.append(f"{relative}: machine_readable must be true")


def validate_relative_links(root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group("target").split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(root)}: broken relative link {target!r}")


def scan_sensitive_content(root: Path, errors: list[str]) -> None:
    ignored_parts = {".git", "__pycache__"}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if any(part in ignored_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(root)}: sensitive indicator {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    validate_public_package(root, errors)
    validate_skill_frontmatter(root, errors)
    validate_agent_metadata(root, errors)
    validate_canonical_assets(root, errors)
    validate_relative_links(root, errors)
    scan_sensitive_content(root, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Skill package validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
