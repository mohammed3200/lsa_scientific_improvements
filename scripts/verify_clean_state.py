#!/usr/bin/env python3
"""
Verify that the project is in a clean state.
Checks for remaining generated artifacts and ensures core files are preserved.
"""

import os
import sys
from pathlib import Path


def count_files(pattern: str) -> int:
    """Count files matching pattern, excluding venvs and source templates."""
    count = 0
    for root, dirs, files in os.walk("."):
        # Skip virtual environments and source template dirs
        dirs[:] = [d for d in dirs if d not in {
            "lsa", "lsa_improvements", "venv", "env", ".git"
        }]
        for f in files:
            if f.endswith(pattern):
                full_path = Path(root) / f
                # Exclude source templates and project HTML
                if "pipeline/templates" in str(full_path) or "lsa_project" in str(full_path):
                    continue
                count += 1
    return count


def check_dir_empty(dir_path: str) -> bool:
    """Check if a directory is empty (no files)."""
    path = Path(dir_path)
    if not path.exists():
        return True
    return len(list(path.iterdir())) == 0


def main():
    print("=" * 60)
    print("LSA Project Clean State Verification")
    print("=" * 60)

    # Check preserved core files
    core_files = [
        "README.md", "CHANGELOG.md", "BASELINE.md",
        "requirements.txt", ".gitignore",
    ]
    core_dirs = [
        "lsa_project", "core", "analysis", "tests",
        "models", "scripts", "pipeline", "proofs",
    ]

    print("\n[1] Core Files Preserved:")
    all_present = True
    for f in core_files:
        exists = Path(f).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {f}")
        if not exists:
            all_present = False

    print("\n[2] Core Directories Preserved:")
    for d in core_dirs:
        exists = Path(d).exists() and Path(d).is_dir()
        status = "✓" if exists else "✗"
        print(f"  {status} {d}/")
        if not exists:
            all_present = False

    # Check for removed artifacts
    print("\n[3] Generated Artifacts Removed:")
    py_files = count_files(".py")
    pyc_files = count_files(".pyc")
    png_files = count_files(".png")
    json_files = count_files(".json")
    csv_files = count_files(".csv")
    html_files = count_files(".html")
    pdf_files = count_files(".pdf")

    print(f"  .py source files:     {py_files} (should be > 0)")
    print(f"  .pyc cache files:     {pyc_files} (should be 0)")
    print(f"  .png image files:     {png_files} (should be 0)")
    print(f"  .json data files:     {json_files} (should be 0)")
    print(f"  .csv data files:      {csv_files} (should be 0)")
    print(f"  .html reports:        {html_files} (should be 0)")
    print(f"  .pdf reports:         {pdf_files} (should be 0)")

    # Check results dirs
    print("\n[4] Results Directories Empty:")
    result_dirs = ["results/raw_data", "results/figures", "results/interactive", "results/reports"]
    for d in result_dirs:
        empty = check_dir_empty(d)
        status = "✓ EMPTY" if empty else "✗ HAS FILES"
        print(f"  {status}: {d}")

    # Overall status
    print("\n" + "=" * 60)
    dirty = (pyc_files > 0 or png_files > 0 or json_files > 0 or
             csv_files > 0 or html_files > 0 or pdf_files > 0)

    if dirty or not all_present:
        print("STATUS: DIRTY — Some artifacts remain or core files missing")
        return 1
    else:
        print("STATUS: CLEAN — Ready for fresh data generation")
        return 0


if __name__ == "__main__":
    sys.exit(main())
