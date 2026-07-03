#!/usr/bin/env python3
"""
generate_changelog.py

Reads git commit history from a repository and produces a categorized
CHANGELOG.md entry in the "Keep a Changelog" style, grouping commits by
type using Conventional Commits prefixes (feat, fix, docs, refactor, etc).

Usage:
    python generate_changelog.py --repo /path/to/repo [--since <rev-or-date>] \
        [--version X.Y.Z] [--out CHANGELOG.md] [--prepend]

Examples:
    # Changelog for everything since the last tag
    python generate_changelog.py --repo . --since "$(git -C . describe --tags --abbrev=0)"

    # Changelog for the last 2 weeks, labeled as version 1.4.0
    python generate_changelog.py --repo . --since "2 weeks ago" --version 1.4.0

    # Changelog for a specific commit range
    python generate_changelog.py --repo . --since v1.2.0..v1.3.0
"""

import argparse
import datetime
import re
import subprocess
import sys
from collections import defaultdict, OrderedDict

# Conventional commit type -> Keep a Changelog section heading
TYPE_MAP = OrderedDict([
    ("feat", "Added"),
    ("fix", "Fixed"),
    ("perf", "Performance"),
    ("refactor", "Changed"),
    ("docs", "Documentation"),
    ("style", "Style"),
    ("test", "Tests"),
    ("build", "Build"),
    ("ci", "CI"),
    ("chore", "Chores"),
    ("revert", "Reverted"),
])

# Order sections should appear in the final changelog
SECTION_ORDER = [
    "Added", "Changed", "Fixed", "Performance", "Documentation",
    "Tests", "Build", "CI", "Reverted", "Style", "Chores", "Other",
]

COMMIT_RE = re.compile(
    r"^(?P<type>\w+)(\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$"
)


def run_git(repo, args):
    result = subprocess.run(
        ["git", "-C", repo] + args,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)
    return result.stdout


def get_commits(repo, since):
    """Return list of (hash, subject, body) for commits in range."""
    fmt = "%H%x1f%s%x1f%b%x1e"
    rev_range = since if since and ".." in since else None
    args = ["log", f"--pretty=format:{fmt}"]
    if rev_range:
        args.append(rev_range)
    elif since:
        args.append(f"--since={since}")
    out = run_git(repo, args)
    commits = []
    for record in out.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f")
        if len(parts) < 2:
            continue
        h, subject = parts[0], parts[1]
        body = parts[2] if len(parts) > 2 else ""
        commits.append((h, subject.strip(), body.strip()))
    return commits


def categorize(commits):
    sections = defaultdict(list)
    breaking = []
    for h, subject, body in commits:
        m = COMMIT_RE.match(subject)
        short_hash = h[:7]
        if m:
            ctype = m.group("type").lower()
            scope = m.group("scope")
            is_breaking = bool(m.group("breaking")) or "BREAKING CHANGE" in body
            desc = m.group("subject").strip()
            if scope:
                desc = f"**{scope}:** {desc}"
            section = TYPE_MAP.get(ctype, "Other")
            entry = f"{desc} ({short_hash})"
            sections[section].append(entry)
            if is_breaking:
                breaking.append(entry)
        else:
            sections["Other"].append(f"{subject.strip()} ({short_hash})")
    return sections, breaking


def render_markdown(sections, breaking, version, date):
    lines = []
    header = f"## [{version}]" if version else "## [Unreleased]"
    header += f" - {date}"
    lines.append(header)
    lines.append("")

    if breaking:
        lines.append("### ⚠ BREAKING CHANGES")
        for item in breaking:
            lines.append(f"- {item}")
        lines.append("")

    for section in SECTION_ORDER:
        items = sections.get(section)
        if not items:
            continue
        lines.append(f"### {section}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate a categorized changelog from git history.")
    parser.add_argument("--repo", default=".", help="Path to the git repository (default: current dir)")
    parser.add_argument("--since", default=None,
                         help="Git revision range (e.g. v1.2.0..v1.3.0) or a date expression (e.g. '2 weeks ago')")
    parser.add_argument("--version", default=None, help="Version label for this changelog entry")
    parser.add_argument("--out", default=None, help="Output file. If omitted, prints to stdout.")
    parser.add_argument("--prepend", action="store_true",
                         help="Prepend the new entry to an existing CHANGELOG.md at --out instead of overwriting")
    args = parser.parse_args()

    commits = get_commits(args.repo, args.since)
    if not commits:
        print("No commits found in the given range.", file=sys.stderr)
        sys.exit(1)

    sections, breaking = categorize(commits)
    date = datetime.date.today().isoformat()
    new_entry = render_markdown(sections, breaking, args.version, date)

    if not args.out:
        print(new_entry)
        return

    if args.prepend:
        try:
            with open(args.out, "r") as f:
                existing = f.read()
        except FileNotFoundError:
            existing = "# Changelog\n\n"
        # Insert new entry right after the top-level "# Changelog" title if present
        if existing.startswith("# Changelog"):
            title, _, rest = existing.partition("\n")
            combined = f"{title}\n\n{new_entry}\n{rest.lstrip(chr(10))}"
        else:
            combined = f"{new_entry}\n{existing}"
        with open(args.out, "w") as f:
            f.write(combined)
    else:
        with open(args.out, "w") as f:
            f.write(f"# Changelog\n\n{new_entry}")

    print(f"Wrote changelog entry to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
