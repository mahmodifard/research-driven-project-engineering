#!/usr/bin/env python3
"""Validate instantiated project controls against the canonical vocabulary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from control_validation import validate_control_directory
except ModuleNotFoundError:  # Supports module-style execution in tests.
    from tools.control_validation import validate_control_directory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="Directory containing canonical project-control YAML")
    parser.add_argument("--vocabulary", required=True, help="Path to control-vocabulary.yaml")
    parser.add_argument("--previous-root", help="Previous control directory for history and transition checks")
    args = parser.parse_args()
    errors = validate_control_directory(
        Path(args.root).resolve(),
        Path(args.vocabulary).resolve(),
        Path(args.previous_root).resolve() if args.previous_root else None,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Project-control validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
