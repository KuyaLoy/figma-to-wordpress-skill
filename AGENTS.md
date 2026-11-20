# AGENTS.md

This repository is the **figma-to-wordpress** skill, packaged as a Claude Code plugin and a one-plugin marketplace.

## Using it

Read `skills/figma-to-wordpress/SKILL.md` and follow it. Detail that only some steps need lives next to it in
`references/`; SKILL.md says when to read each. The scripts are in `skills/figma-to-wordpress/scripts/`. WordPress
builds also use the convert-to-wordpress skill's kit (`references/wordpress.md` says how to find it).

## Changing the skill

- Keep `SKILL.md` under 250 lines and its line width under 120 characters (table rows may be longer). Plain
  English, no dashes as punctuation. Keep it simple: a new step needs a reason from a real build.
- Never copy convert-to-wordpress's WordPress rules here: point at them.
- No real names of people, clients, companies, portals, sites or internal task IDs. Examples use "Example",
  "ABC1-T8" and example.com. Personal details belong in the developer's local profile, never in the skill.
- No password, licence key or API key anywhere in the repo, examples included.
- Keep the progress.json keys stable (`references/progress.md`): other skills may read the same shape. The live
  page's collections and fields (`scripts/live.py`) stay the same as convert-to-wordpress's `live.py`.
- Before a change is done:
  - `claude plugin validate . --strict` passes;
  - `python -m unittest discover -s tests`, `node --check skills/figma-to-wordpress/scripts/check.mjs` and
    `node --test tests/check.test.mjs` pass; a change to check.mjs also runs once on a small local page with one
    planted failure per check;
  - steps stay in plain words that any AI tool can follow; a Claude-only tool gets its fallback next to it;
    the SKILL.md frontmatter keeps only name (equal to the folder), description and license;
  - every changed line is in CHANGELOG.md: a change to the skill or the manifests (`skills/`, `.claude-plugin/`)
    under its new version (see Release), a docs-only change under Unreleased;
  - a private-name scan of the repo and its history finds nothing, commit author and committer names and emails
    included (keep the word list outside the repo; commits use the account's noreply address).
- Release: a merge to main that changes the skill is a release, so main is always a released version.
  1. In the pull request: raise the version in `.claude-plugin/plugin.json` (only there; Semantic Versioning: fix =
     patch, new rule = minor, changed workflow = major) and add its `## [x.y.z] - YYYY-MM-DD` section to CHANGELOG.md
     (move any Unreleased lines into it). The `check` workflow fails a pull request that changes the skill without both.
  2. Run the private-name scan, then merge by fast-forwarding main to the pull request's commits
     (`git push origin <branch>:main`). A squash or merge button stamps a new commit with the GitHub account's email.
  3. The `release` workflow tags `figma-to-wordpress--v<version>` and publishes the GitHub Release with that
     CHANGELOG section. Users with auto-update get it in their next chat; clones with a scheduled pull within days.
  If the workflow fails: `claude plugin tag --push` and a GitHub Release with that CHANGELOG section, by hand.
  Users only get an update when the version changes.
- Licence: MIT.
