#!/usr/bin/env python3
"""Build or verify a reproducibility manifest with hashes and environment metadata."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PACKAGES = (
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "scipy",
    "statsmodels",
    "lifelines",
    "scikit-learn",
    "python-docx",
)

RAW_BYTES_MODE = "raw-bytes"
TEXT_LF_MODE = "text-lf-normalized"
SUPPORTED_CONTENT_MODES = frozenset((RAW_BYTES_MODE, TEXT_LF_MODE))

# These formats are expected to be text in a reproducible analysis package.  The
# list is deliberately extension-based and conservative: container formats such
# as DOCX/XLSX and rendered assets remain byte-exact even though they may contain
# text internally.
TEXT_EXTENSIONS = frozenset(
    {
        ".bat",
        ".bib",
        ".cfg",
        ".cls",
        ".cmd",
        ".conf",
        ".css",
        ".csv",
        ".htm",
        ".html",
        ".ini",
        ".ipynb",
        ".js",
        ".json",
        ".jsonl",
        ".jsx",
        ".log",
        ".md",
        ".ps1",
        ".py",
        ".qmd",
        ".r",
        ".rmd",
        ".rst",
        ".sh",
        ".sql",
        ".sty",
        ".svg",
        ".tex",
        ".toml",
        ".ts",
        ".tsv",
        ".tsx",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the raw-byte SHA-256 digest retained for API compatibility."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_mode_for_path(path: Path) -> str:
    """Choose newline-stable metrics only for known text file extensions."""
    return TEXT_LF_MODE if path.suffix.lower() in TEXT_EXTENSIONS else RAW_BYTES_MODE


def file_metrics(
    path: Path,
    mode: str = RAW_BYTES_MODE,
    chunk_size: int = 1024 * 1024,
) -> tuple[int, str]:
    """Return size and SHA-256 using raw bytes or canonical LF newlines.

    Text normalization is performed on bytes so encoding and all non-newline
    content remain untouched.  A pending carriage return is carried across read
    boundaries, making CRLF normalization stable regardless of ``chunk_size``.
    """
    if mode not in SUPPORTED_CONTENT_MODES:
        raise ValueError(f"Unsupported content mode: {mode!r}")

    digest = hashlib.sha256()
    size = 0
    pending_cr = False
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            if mode == TEXT_LF_MODE:
                if pending_cr:
                    chunk = b"\r" + chunk
                    pending_cr = False
                if chunk.endswith(b"\r"):
                    chunk = chunk[:-1]
                    pending_cr = True
                chunk = chunk.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            digest.update(chunk)
            size += len(chunk)

    if pending_cr:
        digest.update(b"\n")
        size += 1
    return size, digest.hexdigest()


def file_entry(path: Path, base: Path) -> dict:
    resolved = path.resolve()
    try:
        display = str(resolved.relative_to(base.resolve()))
    except ValueError:
        try:
            display = os.path.relpath(resolved, base.resolve())
        except ValueError:  # different drives on Windows
            display = str(resolved)
    display = Path(display).as_posix()
    content_mode = content_mode_for_path(resolved)
    size_bytes, sha256 = file_metrics(resolved, mode=content_mode)
    return {
        "path": display,
        "size_bytes": size_bytes,
        "size_mode": content_mode,
        "sha256": sha256,
        "hash_mode": content_mode,
    }


def _base_directory_for_manifest(base: Path, manifest_path: Path | None) -> str:
    """Serialize a base directory so it is resolvable from the manifest location."""
    resolved_base = base.resolve()
    if manifest_path is None:
        return resolved_base.as_posix()
    manifest_dir = manifest_path.resolve().parent
    try:
        relative = os.path.relpath(resolved_base, manifest_dir)
    except ValueError:  # different drives on Windows
        return resolved_base.as_posix()
    return Path(relative).as_posix()


def resolve_base_directory(
    manifest_path: Path,
    manifest: dict,
    base_override: Path | None = None,
) -> Path:
    """Resolve a manifest's base path using the manifest directory as the anchor."""
    if base_override is not None:
        return base_override.resolve()
    stored = manifest.get("base_directory")
    if not isinstance(stored, str) or not stored.strip():
        raise ValueError("Manifest base_directory must be a non-empty string")
    candidate = Path(stored)
    if candidate.is_absolute():
        return candidate.resolve()
    return (manifest_path.resolve().parent / candidate).resolve()


def package_versions(names=DEFAULT_PACKAGES) -> dict:
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def build_manifest(
    base: Path,
    groups: dict[str, list[Path]],
    status: str,
    note: str = "",
    manifest_path: Path | None = None,
) -> dict:
    return {
        "manifest_version": 3,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "note": note,
        "base_directory": _base_directory_for_manifest(base, manifest_path),
        "files": {
            group: [file_entry(path, base) for path in paths]
            for group, paths in groups.items()
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "packages": package_versions(),
        },
    }


def verify_manifest(manifest_path: Path, base_override: Path | None = None) -> dict:
    """Check every recorded file using its declared size and hash modes.

    Entries created before manifest v3 have no mode fields and therefore retain
    their original raw-byte verification behavior.
    """
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Manifest root must be a JSON object")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("Manifest files must be an object of file groups")

    base = resolve_base_directory(manifest_path, manifest, base_override=base_override)
    results = []
    summary = {
        "total": 0,
        "ok": 0,
        "missing": 0,
        "size_mismatch": 0,
        "sha256_mismatch": 0,
        "invalid_entry": 0,
    }

    for group, entries in files.items():
        if not isinstance(entries, list):
            raise ValueError(f"Manifest file group {group!r} must be a list")
        for entry in entries:
            summary["total"] += 1
            item = {"group": str(group), "path": None, "ok": False, "issues": []}
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                item["issues"].append("invalid_entry")
                summary["invalid_entry"] += 1
                results.append(item)
                continue

            display_path = entry["path"]
            item["path"] = display_path
            recorded_path = Path(display_path)
            resolved_path = (
                recorded_path.resolve()
                if recorded_path.is_absolute()
                else (base / recorded_path).resolve()
            )
            item["resolved_path"] = resolved_path.as_posix()
            item["expected_size_bytes"] = entry.get("size_bytes")
            item["expected_sha256"] = entry.get("sha256")
            size_mode = entry.get("size_mode", RAW_BYTES_MODE)
            hash_mode = entry.get("hash_mode", RAW_BYTES_MODE)
            item["size_mode"] = size_mode
            item["hash_mode"] = hash_mode

            if not resolved_path.is_file():
                item["issues"].append("missing")
                summary["missing"] += 1
                results.append(item)
                continue

            valid_modes = (
                isinstance(size_mode, str)
                and size_mode in SUPPORTED_CONTENT_MODES
                and isinstance(hash_mode, str)
                and hash_mode in SUPPORTED_CONTENT_MODES
            )
            valid_expected = isinstance(entry.get("size_bytes"), int) and isinstance(
                entry.get("sha256"), str
            )
            if not valid_modes or not valid_expected:
                item["issues"].append("invalid_entry")
                summary["invalid_entry"] += 1
            else:
                metrics = {
                    mode: file_metrics(resolved_path, mode=mode)
                    for mode in {size_mode, hash_mode}
                }
                actual_size = metrics[size_mode][0]
                actual_sha256 = metrics[hash_mode][1]
                item["actual_size_bytes"] = actual_size
                item["actual_sha256"] = actual_sha256
                if actual_size != entry["size_bytes"]:
                    item["issues"].append("size_mismatch")
                    summary["size_mismatch"] += 1
                if actual_sha256.lower() != entry["sha256"].lower():
                    item["issues"].append("sha256_mismatch")
                    summary["sha256_mismatch"] += 1

            item["ok"] = not item["issues"]
            if item["ok"]:
                summary["ok"] += 1
            results.append(item)

    base_exists = base.is_dir()
    return {
        "verification_version": 1,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest_path.as_posix(),
        "base_directory": base.as_posix(),
        "base_directory_exists": base_exists,
        "ok": base_exists and summary["ok"] == summary["total"],
        "summary": summary,
        "files": results,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path("."))
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--script", type=Path, action="append", default=[])
    parser.add_argument("--result", type=Path, action="append", default=[])
    parser.add_argument("--asset", type=Path, action="append", default=[])
    parser.add_argument(
        "--status",
        choices=("draft", "needs-author-decision", "approved", "final"),
        default="draft",
    )
    parser.add_argument("--note", default="")
    parser.add_argument("--output", type=Path, default=Path("manifest.json"))
    return parser


def _verify_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analysis_manifest.py verify",
        description="Verify existence, declared size, and SHA-256 for every manifest entry.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--base",
        type=Path,
        help="Optional base-directory override for relocating an analysis package",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON verification-report path")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in {"verify", "--verify"}:
        args = _verify_parser().parse_args(arguments[1:])
        try:
            report = verify_manifest(args.manifest, base_override=args.base)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Verification failed: {exc}", file=sys.stderr)
            return 2
        rendered = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(args.output)
        else:
            print(rendered)
        return 0 if report["ok"] else 1

    if arguments and arguments[0] in {"build", "create"}:
        arguments = arguments[1:]
    args = _build_parser().parse_args(arguments)

    groups = {
        "inputs": args.input,
        "scripts": args.script,
        "results": args.result,
        "assets": args.asset,
    }
    missing = [str(path) for paths in groups.values() for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Manifest paths do not exist: {missing}")

    manifest = build_manifest(
        args.base,
        groups,
        status=args.status,
        note=args.note,
        manifest_path=args.output,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
