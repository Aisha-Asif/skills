# Conventional Commits Reference

This skill categorizes commits based on the [Conventional Commits](https://www.conventionalcommits.org/) prefix format:

```
<type>(<optional scope>)!: <subject>
```

## Recognized types and their changelog section

| Prefix      | Changelog Section |
|-------------|--------------------|
| `feat`      | Added              |
| `fix`       | Fixed              |
| `perf`      | Performance        |
| `refactor`  | Changed            |
| `docs`      | Documentation      |
| `style`     | Style              |
| `test`      | Tests              |
| `build`     | Build              |
| `ci`        | CI                 |
| `chore`     | Chores             |
| `revert`    | Reverted           |
| (anything else) | Other          |

## Breaking changes

A commit is flagged as a breaking change if:
- It has a `!` right before the colon, e.g. `feat(api)!: remove legacy endpoint`, or
- Its commit body contains the literal text `BREAKING CHANGE`

Breaking changes are pulled into their own "⚠ BREAKING CHANGES" section at the top of the entry, in addition to appearing in their normal category.

## If commits don't follow Conventional Commits

If a repo's history is mostly free-form commit messages (no `feat:`, `fix:`, etc. prefixes), the script will put everything under an "Other" section. In that case, before running the script, offer to:

1. Just generate the changelog anyway under "Other" (fast, but unsorted), or
2. Read the raw commit list yourself and manually sort commits into Added / Changed / Fixed / etc. based on their content, then write the changelog directly rather than relying on the script's categorization.

Option 2 usually produces a much better result for repos without commit conventions.
