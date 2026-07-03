# Generating Changelogs — Claude Agent Skill

A Claude [Agent Skill](https://docs.claude.com) that turns a git repository's raw commit
history into a clean, categorized changelog entry, following the
[Keep a Changelog](https://keepachangelog.com/) format.

Point Claude at a repo, tell it what range of commits to cover, and it will produce a
ready-to-paste `CHANGELOG.md` entry — grouped into sections like **Added**, **Fixed**,
**Changed**, and **⚠ BREAKING CHANGES** — instead of a flat, unsorted `git log`.

## What it does

- Reads commit history from any local git repository (no commits or pushes — read-only).
- Parses [Conventional Commits](https://www.conventionalcommits.org/) prefixes
  (`feat`, `fix`, `docs`, `refactor`, `perf`, `chore`, etc.) and maps each one to the
  matching Keep a Changelog section.
- Flags breaking changes (`!` before the colon, or a `BREAKING CHANGE` footer) into their
  own callout section at the top of the entry.
- Supports scoping by tag range, date, or explicit commit range (`v1.2.0..v1.3.0`).
- Can print the new entry for review, or write/prepend it straight into `CHANGELOG.md`.
- Falls back gracefully for repos that don't use Conventional Commits: Claude reads the
  raw messages and categorizes them manually instead of relying purely on the script.

## How it works

This is a Claude **Skill** — a folder of instructions and helper code that Claude loads
automatically when it recognizes a relevant request (e.g. "generate a changelog for this
repo" or "summarize what changed since the last release").

```
generating-changelogs/
├── SKILL.md                        # Instructions Claude follows: workflow, when to
│                                    # trigger, how to invoke the script, review steps
├── scripts/
│   └── generate_changelog.py       # Standalone Python script that reads git history
│                                    # and renders the categorized Markdown entry
└── references/
    └── commit_conventions.md       # Full Conventional Commits prefix table and
                                     # guidance for non-conventional repos
```

**Workflow Claude follows (defined in `SKILL.md`):**

1. Confirm the repo path and commit range (defaults to "since the last git tag").
2. Sample recent commit subjects to check whether the repo follows Conventional Commits.
3. Run `generate_changelog.py` to produce a first-pass, categorized entry.
4. Review the output: merge duplicates, drop noise commits (typos, WIP, merges), and
   make sure breaking changes are called out clearly.
5. Present the final entry — or the diff, if updating an existing `CHANGELOG.md` — to the user.

## Example

```bash
python3 scripts/generate_changelog.py \
  --repo . \
  --since "$(git describe --tags --abbrev=0)" \
  --version 1.4.0 \
  --out CHANGELOG.md \
  --prepend
```

Produces an entry like:

```markdown
## [1.4.0] - 2026-07-03

### ⚠ BREAKING CHANGES
- **api:** remove legacy v1 endpoint (a1b2c3d)

### Added
- **auth:** add OAuth2 login support (9f8e7d6)

### Fixed
- correct off-by-one error in pagination (4c5d6e7)
```

## Usage

Copy the `generating-changelogs/` folder into your Claude Skills directory (or upload it
as a Skill in Claude), then simply ask Claude something like:

> "Generate a changelog for this repo since the last tag."
>
> "Summarize what changed here over the last 2 weeks."
>
> "Prepare release notes for v2.0.0."

Claude will load the skill automatically, run the script, review the results, and present
the finished changelog entry.

## Project links

- **GitHub repository:** [ADD LINK HERE]
- **Course / assignment:** [ADD LINK HERE]

## About

Built as a submission for [COURSE NAME — ADD LINK/DETAILS HERE], demonstrating how to
package a reusable workflow (git history → categorized changelog) as a Claude Agent Skill.
