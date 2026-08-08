#!/usr/bin/env python3
"""PreToolUse guard for the owner-only files.

Enforces two invariants from docs/SPEC.md structurally, so they hold no matter
what any agent's brief says:

  1. data/Research/{TICKER}.md is APPEND-ONLY. A full-file Write is refused
     (except when creating a file that does not exist yet); an Edit is refused
     unless it is a pure insertion (old_string survives verbatim inside
     new_string).
  2. data/Watchlist.md is never overwritten wholesale. Row-level Edits still
     pass -- those are the documented, owner-confirmed path.

Blocks with exit code 2; stderr is fed back to the calling agent.
"""

import json
import os
import re
import sys

RESEARCH_DIR = os.path.join("data", "Research")
WATCHLIST = os.path.join("data", "Watchlist.md")


def classify(path: str, cwd: str) -> str:
    """Return 'research', 'watchlist', or '' for a target path."""
    if not path:
        return ""
    abs_path = os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))
    if os.sep + RESEARCH_DIR + os.sep in abs_path + os.sep:
        return "research"
    if abs_path.endswith(os.sep + WATCHLIST):
        return "watchlist"
    return ""


def deny(message: str) -> None:
    sys.stderr.write(message.strip() + "\n")
    sys.exit(2)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never break the session on a malformed payload

    tool = payload.get("tool_name", "")
    args = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()

    if tool == "Bash":
        command = args.get("command", "")
        # Only fire when a mutation operator actually TARGETS the path -- merely
        # mentioning it (grep, git add, a --json arg) must stay allowed.
        owned = r"[^\s'\"]*(?:data/Research/[^\s'\"]+|data/Watchlist\.md)"
        targets = re.findall(
            r"(?:>>?|(?:^|\s)tee(?:\s+-\w+)*|(?:^|\s)(?:sed|perl)\s+[^|;&]*?-i[^|;&]*?"
            rf"|(?:^|\s)truncate\s+[^|;&]*?)\s*({owned})",
            command,
        )
        if targets:
            deny(
                "BLOCKED: shell redirection/in-place edit against an owner-only file "
                f"({', '.join(sorted(set(targets)))}).\n"
                "data/Research/ is append-only and data/Watchlist.md is owner-confirmed. "
                "Use the Edit tool for a pure append, or hand the change to the main "
                "session -- see docs/SPEC.md, 'Owner-only files'."
            )
        sys.exit(0)

    kind = classify(args.get("file_path", ""), cwd)
    if not kind:
        sys.exit(0)

    if tool == "Write":
        abs_path = os.path.normpath(
            os.path.join(cwd, os.path.expanduser(args.get("file_path", "")))
        )
        if kind == "research" and not os.path.exists(abs_path):
            sys.exit(0)  # creating a new thesis file is documented in SPEC.md
        deny(
            f"BLOCKED: Write would overwrite an owner-only file ({args.get('file_path')}).\n"
            + (
                "data/Research/ is the owner's append-only audit trail. Append with the "
                "Edit tool instead: old_string must reappear verbatim inside new_string. "
                "Agents may add ONLY the dated one-line report pointer."
                if kind == "research"
                else "data/Watchlist.md is never rewritten wholesale. Edit the single row, "
                "and only after the owner confirms the change."
            )
            + "\nSee docs/SPEC.md, 'Owner-only files'."
        )

    if tool == "Edit" and kind == "research":
        old = args.get("old_string", "")
        new = args.get("new_string", "")
        if args.get("replace_all"):
            deny(
                "BLOCKED: replace_all on an append-only file "
                f"({args.get('file_path')}). Target one anchor and append after it."
            )
        if old and old not in new:
            deny(
                f"BLOCKED: this Edit rewrites existing content in {args.get('file_path')}.\n"
                "data/Research/ is append-only -- the audit trail is the point. An allowed "
                "edit keeps old_string verbatim inside new_string and adds after it. "
                "To genuinely revise past text, the owner does it by hand.\n"
                "See docs/SPEC.md, 'Owner-only files'."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
