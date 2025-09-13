# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
"""
Guard test ensuring any future introduction of jwt.decode() calls explicitly
specifies an algorithms= [...] (or similar) argument.

Rationale:
    PyJWT 2.x requires explicit specification of acceptable algorithms to
    avoid security pitfalls (algorithm confusion / accepting "none" or an
    unexpected default). At present the codebase contains no calls to
    jwt.decode(). This test enforces that if such calls are added later,
    they include an algorithms= keyword argument.

Behavior:
    - Scans all first-party Python sources under lftools_uv/.
    - Locates occurrences of the token sequence 'jwt.decode('.
    - For each occurrence, inspects a window of subsequent characters to
      verify the presence of 'algorithms=' before the closing parenthesis
      of that call expression (heuristically, within a fixed window).
    - Fails the test with a helpful message listing offending file/line(s).

Limitations (acceptable for a lightweight guard):
    - Simple textual scan; does not build an AST or handle nested parentheses
      perfectly in pathological formatting cases—adequate for our style.
    - If a call is split unusually and the 'algorithms=' appears more than
      WINDOW characters away, the test may falsely flag it; adjust WINDOW
      if needed.

If a legitimate decode call is added:
    Example (secure pattern):
        jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience="expected-aud",
        )

    Avoid:
        jwt.decode(token, key)
"""

from __future__ import annotations

import pathlib
import re

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent / "lftools_uv"
# Heuristic window size to search after 'jwt.decode(' for algorithms=
WINDOW = 400

# Precompiled regex for performance when scanning many files
DECODE_PATTERN = re.compile(r"jwt\.decode\s*\(", re.MULTILINE)


def _find_insecure_jwt_decodes() -> list[tuple[pathlib.Path, int, str]]:
    """
    Scan project Python files for jwt.decode usages lacking an algorithms= kwarg.

    Returns:
        List of tuples: (file_path, line_number, line_content_trimmed)
    """
    offenders: list[tuple[pathlib.Path, int, str]] = []

    if not SOURCE_ROOT.exists():
        # Safety fallback; if layout changes the test should not explode
        return offenders

    for py_file in SOURCE_ROOT.rglob("*.py"):
        # Skip generated / cache directories defensively, though pattern excludes them
        if any(part.startswith("__pycache__") for part in py_file.parts):
            continue

        try:
            text = py_file.read_text(encoding="utf-8")
        except OSError:
            continue  # Ignore unreadable files (unlikely in repo)

        for match in DECODE_PATTERN.finditer(text):
            start_index = match.start()
            window_slice = text[start_index : start_index + WINDOW]

            # Quick heuristic: if 'algorithms=' appears before a closing paren that
            # would plausibly terminate THIS call, accept it. We don't attempt to
            # fully match parentheses—good enough for normal formatting.
            if "algorithms=" in window_slice:
                continue

            # Determine line number (1-based) for reporting
            line_number = text.count("\n", 0, start_index) + 1
            line_content = text.splitlines()[line_number - 1].strip()

            offenders.append((py_file, line_number, line_content))

    return offenders


def test_no_insecure_jwt_decode_usage() -> None:
    """
    Ensure no jwt.decode() calls are introduced without an explicit algorithms=.
    """
    offenders = _find_insecure_jwt_decodes()
    if offenders:
        lines = "\n".join(f" - {path}:{line_num}: {snippet}" for path, line_num, snippet in offenders)
        raise AssertionError(
            "Found jwt.decode() calls without an explicit 'algorithms=' keyword:\n"
            f"{lines}\n\n"
            "Remediation: Add an explicit algorithms=[...] argument to each "
            "jwt.decode() invocation (e.g., algorithms=['RS256'])."
        )
