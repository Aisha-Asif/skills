---
name: generating-changelogs
description: Generate a categorized, human-readable CHANGELOG.md entry from a git repository's commit history, following the "Keep a Changelog" format. Use this skill whenever the user asks to write, update, or generate a changelog, release notes, or "what changed" summary for a git repo, or mentions preparing for a release/tag and wants the commit history turned into something readable. Also trigger if the user asks to summarize recent commits, list changes since the last tag/release, or organize commits by type (features, fixes, docs, etc). Works on any local git repository.
---

# Generating Changelogs

Turns raw git commit history into a clean, categorized changelog entry that's ready to paste into `CHANGELOG.md` or a release notes page.

## When to use this

Use this skill whenever the user wants to:
- Generate/update a `CHANGELOG.md` for a repo
- Summarize "what changed" since the last release, tag, or a given date
- Prepare release notes for a new version
- Turn a messy commit history into an organized list grouped by type (Added / Fixed / Changed / etc.)

## Workflow

1. **Confirm the repo and range.** Figure out:
   - The path to the git repository (ask if not obvious, or use the current working directory if the user is clearly working in one repo)
   - The range of commits to include — since the last tag, since a date ("2 weeks ago"), a specific commit range (`v1.2.0..v1.3.0`), or "all history"
   - Whether this changelog entry should be labeled with a version number (e.g. `1.4.0`) or left as `[Unreleased]`

   If the user hasn't specified, a good default is "commits since the most recent git tag." You can find the most recent tag with:
   ```bash
   git -C <repo> describe --tags --abbrev=0
   ```
   If there are no tags, default to the full history or ask the user for a reasonable starting point (e.g. last 30 days).

2. **Check whether the repo uses Conventional Commits.** Peek at a handful of recent commit subjects:
   ```bash
   git -C <repo> log --oneline -20
   ```
   See `references/commit_conventions.md` for the full prefix reference and for what to do if the repo does *not* follow Conventional Commits (in which case, read the commits yourself and categorize them manually rather than relying purely on the script).

3. **Run the generator script.**
   ```bash
   python3 scripts/generate_changelog.py --repo <repo> --since <range-or-date> [--version X.Y.Z] --out CHANGELOG.md --prepend
   ```
   - Omit `--out` to just print the new entry to stdout for review first — recommended for the first pass so you and the user can check it before writing to disk.
   - Use `--prepend` once the user is happy, so the new entry gets added above the existing changelog content rather than overwriting it.
   - Use `--version X.Y.Z` if this is a tagged release; otherwise the entry is labeled `[Unreleased]`.

4. **Review and clean up.** The script does the mechanical grouping, but always read the output before presenting it:
   - Merge or reword duplicate/near-duplicate entries
   - Drop noise commits (e.g. `chore: typo`, merge commits, WIP commits) if they clutter the changelog
   - If many commits landed in "Other" because they don't follow Conventional Commits, manually sort the important ones into the right section (see step 2)
   - Make sure breaking changes are clearly called out at the top

5. **Present the result.** Show the final changelog entry to the user (or the diff, if updating an existing file), and if a `CHANGELOG.md` file was written, let them know where it is.

## Notes

- The script only reads git history — it never commits or pushes anything. All writes are limited to the changelog file the user specifies.
- Squash-merged PRs often produce one commit per PR with a good conventional-commit-style title — this tends to produce the cleanest changelogs.
- For repos with many contributors and inconsistent commit styles, lean more on manual review (step 4) than the raw script output.
