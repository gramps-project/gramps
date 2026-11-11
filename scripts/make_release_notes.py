#!/usr/bin/env python3
"""
Generate formatted Gramps release notes from GitHub release data.

Fetches the release body and commit history via the gh CLI, resolves GitHub
usernames for any commits whose author couldn't be matched, then calls an
LLM via litellm to produce categorised, author-attributed release notes in
the project's standard Markdown format.

Fetched GitHub data is saved to RELEASE_DATA_<version>.json and reused on
subsequent runs, so re-runs with a different model or modified prompt skip
all GitHub API calls.  Use --no-cache to force a fresh fetch.

Optionally appends a section listing open PRs/issues targeted at a milestone
but not yet merged (--milestone <number>).

Requirements:
    gh CLI authenticated (gh auth login)
    pip install litellm
    ANTHROPIC_API_KEY or GOOGLE_API_KEY etc. set in environment

Usage:
    # First run — fetches from GitHub, saves cache, generates notes
    python3 scripts/make_release_notes.py --to-tag v6.1.0-beta1 --from-tag v6.0.7

    # --to-tag defaults to the latest tag in the same major.minor series
    python3 scripts/make_release_notes.py --from-tag v6.0.7

    # Re-run — loads cache automatically, no GitHub calls
    python3 scripts/make_release_notes.py --to-tag v6.1.0-beta1

    # Re-run with a different model
    python3 scripts/make_release_notes.py --to-tag v6.1.0-beta1 --model gemini/gemini-2.5-flash

    # Force re-fetch and overwrite cache
    python3 scripts/make_release_notes.py --to-tag v6.1.0-beta1 --from-tag v6.0.7 --no-cache

    # Notes between any two arbitrary tags
    python3 scripts/make_release_notes.py --from-tag v6.0.5 --to-tag v6.0.6

    # Wildcards work on both --from-tag and --to-tag
    python3 scripts/make_release_notes.py --from-tag "6.0.*" --to-tag "6.1.*"
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path


def gh(*args):
    result = subprocess.run(
        ["gh"] + list(args),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_release_body(tag, repo):
    return gh("release", "view", tag, "--repo", repo, "--json", "body", "--jq", ".body")


def get_commits(from_tag, to_tag, repo):
    jq = (
        ".commits[] | "
        "{sha: .sha[0:8], "
        " author: .author.login, "
        ' message: (.commit.message | split("\\n")[0])}'
    )
    output = gh("api", f"repos/{repo}/compare/{from_tag}...{to_tag}", "--jq", jq)
    commits = []
    for line in output.splitlines():
        line = line.strip()
        if line:
            commits.append(json.loads(line))
    return commits


def resolve_author_via_pr(sha, repo):
    """Find the PR that introduced this commit and return its author login."""
    try:
        output = gh(
            "api",
            f"repos/{repo}/commits/{sha}/pulls",
            "--jq",
            ".[0].user.login",
        )
        return output.strip() or None
    except subprocess.CalledProcessError:
        return None


def resolve_null_authors(commits, repo):
    """Fill in missing author logins by looking up the associated PR."""
    for commit in commits:
        if commit["author"] is None:
            author = resolve_author_via_pr(commit["sha"], repo)
            if author:
                commit["author"] = author
                print(
                    f"  resolved @{author} for: {commit['message'][:60]}",
                    file=sys.stderr,
                )
    return commits


SKIP_PATTERNS = re.compile(
    r"^(Merge (branch|pull request)|"
    r"Translated using Weblate|"
    r"Update translation files|"
    r"Set to development version|"
    r"Release Gramps|"
    r"Update (gramps\.pot|ChangeLog|NEWS|copyright)|"
    r"Unrelated formatting|"
    r"Fix code formatting|"
    r"Small one-line fixes|"
    r"Code improvements|"
    r"Remove out of date comments|"
    r"Fix spelling mistake)",
    re.IGNORECASE,
)


def filter_commits(commits):
    return [c for c in commits if not SKIP_PATTERNS.match(c["message"])]


def save_cache(
    path, tag, from_tag, repo, release_date, release_body, commits, milestone_items
):
    """Save fetched GitHub data to a JSON file for later re-use."""
    data = {
        "tag": tag,
        "from_tag": from_tag,
        "repo": repo,
        "release_date": release_date,
        "release_body": release_body,
        "commits": commits,
        "milestone_items": milestone_items,
    }
    path.write_text(json.dumps(data, indent=2))
    print(f"Cache saved to {path}", file=sys.stderr)


def load_cache(path):
    """Load previously fetched GitHub data from a JSON file."""
    if not path.exists():
        print(f"ERROR: cache file not found: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text())
    print(f"Loaded cache from {path}", file=sys.stderr)
    return data


EXAMPLE_OUTPUT = """
## New Features

### UI Enhancements
- **Favorites sidebar**: Add a favorites sidebar and persistent sidebar for all views ([#2091](https://github.com/gramps-project/gramps/pull/2091)) — ***SNoiraud***

## Bug Fixes

### Data & Calculations
- **sort_key**: Replace `hexlify` with `getSortKey()` bytes, drop `binascii` import ([Bug #10077](https://gramps-project.org/bugs/view.php?id=10077)) — ***dsblank***

## Translations

Updated: da, es, fr, hr.
""".strip()

DEFAULT_MODEL = "anthropic/claude-opus-4-7"


def generate_notes(release_body, commits, tag, repo, release_date, model):
    """Call an LLM via litellm to produce Markdown release notes."""
    try:
        import litellm
    except ImportError:
        print(
            "ERROR: 'litellm' package not installed. Run: pip install litellm",
            file=sys.stderr,
        )
        sys.exit(1)

    commit_lines = "\n".join(
        f"- [{c['sha']}] @{c['author'] or 'unknown'}: {c['message']}" for c in commits
    )

    prompt = f"""You are generating release notes for Gramps genealogy software.

Release: {tag}
Repo: https://github.com/{repo}
Date: {release_date}

GitHub release body (contains the official bullet list):
<release_body>
{release_body}
</release_body>

Commits with GitHub author logins (use these to attribute each item):
<commits>
{commit_lines}
</commits>

Write Markdown release notes following this exact structure:

1. `# Gramps {{version}} — Release Notes ({{date}})`
2. One short intro paragraph (2-3 sentences).
3. `> **Always [back up...]** ...` blockquote.
4. Note if this release includes fixes from a prior maintenance release.
5. `---` separator then sections:
   - **New Features** with sub-sections by area (e.g. UI Enhancements, Filters, Reports & NarrativeWeb)
   - **Bug Fixes** with sub-sections (e.g. Data & Calculations, UI & Editing, Windows)
   - **Build System & Type Checking** (if relevant)
   - **Testing** (if relevant)
   - **Translations** (list language codes updated)

Format each item as:
`- **Label**: Description ([#PR](url) or [Bug #N](url)) — ***@author***`

Rules:
- Use `https://gramps-project.org/bugs/view.php?id=NNNNN` for bug tracker links.
- Use `https://github.com/{repo}/pull/NNN` for PR links.
- Skip merge commits, translation commits, and trivial cleanup.
- Match authors from the commits list. If a commit message mentions a bug number or PR, include the link.
- Group related items; don't list every trivial commit separately.

Example item format:
{EXAMPLE_OUTPUT}

Output only the Markdown. No preamble, no explanation."""

    print(f"Calling {model}...", file=sys.stderr)
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def get_milestone_open_items(milestone, repo):
    """Return open PRs and issues assigned to the given milestone number."""
    items = []
    page = 1
    while True:
        output = gh(
            "api",
            f"repos/{repo}/issues?milestone={milestone}&state=open&per_page=100&page={page}",
            "--jq",
            ".[] | {number, title, is_pr: (.pull_request != null),"
            " labels: [.labels[].name], user: .user.login}",
        )
        batch = []
        for line in output.splitlines():
            line = line.strip()
            if line:
                batch.append(json.loads(line))
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def format_milestone_section(items, repo):
    """Return a Markdown section listing open milestone items."""
    if not items:
        return ""

    prs = [i for i in items if i["is_pr"]]
    issues = [i for i in items if not i["is_pr"]]

    lines = ["\n---\n", "## Targeted for This Release (Not Yet Merged)\n"]
    lines.append(
        "_The following pull requests and issues are milestoned for this release "
        "but have not been merged yet._\n"
    )

    if prs:
        lines.append("### Open Pull Requests\n")
        for item in sorted(prs, key=lambda x: x["number"]):
            url = f"https://github.com/{repo}/pull/{item['number']}"
            label_str = (
                " `" + "` `".join(item["labels"]) + "`" if item["labels"] else ""
            )
            lines.append(
                f"- [#{item['number']}]({url}) {item['title']}"
                f"{label_str} — ***@{item['user']}***"
            )

    if issues:
        lines.append("\n### Open Issues\n")
        for item in sorted(issues, key=lambda x: x["number"]):
            url = f"https://github.com/{repo}/issues/{item['number']}"
            label_str = (
                " `" + "` `".join(item["labels"]) + "`" if item["labels"] else ""
            )
            lines.append(
                f"- [#{item['number']}]({url}) {item['title']}"
                f"{label_str} — ***@{item['user']}***"
            )

    return "\n".join(lines) + "\n"


def version_key(tag):
    """Sort key for version tags: by numeric components, releases above pre-releases."""
    base = tag.split("-")[0]  # strip pre-release suffix (e.g. -beta1, -rc1)
    nums = tuple(int(n) for n in re.findall(r"\d+", base))
    return (nums, "-" not in tag)


def fetch_all_tags(repo):
    """Return all tag names for a GitHub repo."""
    tags = []
    page = 1
    while True:
        output = gh(
            "api",
            f"repos/{repo}/tags?per_page=100&page={page}",
            "--jq",
            "[.[].name]",
        )
        batch = json.loads(output)
        tags.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return tags


def get_latest_tag_in_series(from_tag, repo):
    """Return the newest tag sharing the same major.minor version as from_tag."""
    match = re.match(r"^v?(\d+)\.(\d+)", from_tag)
    if not match:
        return None
    prefix = f"v{match.group(1)}.{match.group(2)}."
    series = [t for t in fetch_all_tags(repo) if t.startswith(prefix)]
    return sorted(series, key=version_key)[-1] if series else None


def resolve_wildcard_tag(pattern, repo):
    """Return the newest tag matching a glob pattern such as '6.1.*' or 'v6.1.*'."""
    if not pattern.startswith("v"):
        pattern = "v" + pattern
    matches = [t for t in fetch_all_tags(repo) if fnmatch.fnmatch(t, pattern)]
    return sorted(matches, key=version_key)[-1] if matches else None


def dump_raw(release_body, commits, tag, milestone_items=None):
    print(f"=== Release body for {tag} ===\n")
    print(release_body)
    print(f"\n=== {len(commits)} commits (after filtering) ===\n")
    for c in commits:
        print(f"  [{c['sha']}] @{c['author'] or '?':20s}  {c['message']}")
    if milestone_items is not None:
        print(f"\n=== {len(milestone_items)} open milestone items ===\n")
        for item in milestone_items:
            kind = "PR" if item["is_pr"] else "Issue"
            print(f"  [{kind} #{item['number']}] @{item['user']:20s}  {item['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Gramps release notes using gh CLI + an LLM via litellm"
    )
    parser.add_argument(
        "--to-tag",
        default=None,
        help=(
            "Release tag, e.g. v6.1.0-beta1. Accepts glob patterns such as '6.1.*' "
            "(resolves to the newest matching tag). "
            "Defaults to the latest tag in the same major.minor series as --from-tag."
        ),
    )
    parser.add_argument(
        "--from-tag",
        default=None,
        help=(
            "Previous release tag, e.g. v6.0.7 (required when no cache exists). "
            "Accepts glob patterns such as '6.0.*' (resolves to the newest matching tag)."
        ),
    )
    parser.add_argument(
        "--repo", default="gramps-project/gramps", help="GitHub repo (owner/name)"
    )
    parser.add_argument(
        "--output",
        help="Output file (default: RELEASE_NOTES_<version>.md in cwd)",
    )
    parser.add_argument(
        "--dump-only",
        action="store_true",
        help="Print raw data instead of calling the LLM",
    )
    parser.add_argument(
        "--release-date",
        help="Override release date (default: taken from gh release view)",
    )
    parser.add_argument(
        "--milestone",
        help="GitHub milestone number; appends a section of open (not-yet-merged) items",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=(
            f"LLM model string passed to litellm (default: {DEFAULT_MODEL}). "
            "Examples: gemini/gemini-2.5-flash, anthropic/claude-sonnet-4-6"
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore any existing cache and re-fetch from GitHub (requires --from-tag)",
    )
    args = parser.parse_args()

    from_tag = args.from_tag
    if from_tag and ("*" in from_tag or "?" in from_tag):
        print(f"Resolving wildcard pattern {from_tag!r}...", file=sys.stderr)
        from_tag = resolve_wildcard_tag(from_tag, args.repo)
        if not from_tag:
            parser.error(f"No tags matched pattern {args.from_tag!r} in {args.repo}")
        print(f"  Using --from-tag {from_tag}", file=sys.stderr)

    to_tag = args.to_tag
    if to_tag and ("*" in to_tag or "?" in to_tag):
        print(f"Resolving wildcard pattern {to_tag!r}...", file=sys.stderr)
        to_tag = resolve_wildcard_tag(to_tag, args.repo)
        if not to_tag:
            parser.error(f"No tags matched pattern {args.to_tag!r} in {args.repo}")
        print(f"  Using --to-tag {to_tag}", file=sys.stderr)
    elif not to_tag:
        if not from_tag:
            parser.error("--to-tag or --from-tag is required")
        print(f"Resolving latest tag in series from {from_tag}...", file=sys.stderr)
        to_tag = get_latest_tag_in_series(from_tag, args.repo)
        if not to_tag:
            parser.error(
                f"No tags found in the same series as {from_tag} in {args.repo}"
            )
        print(f"  Using --to-tag {to_tag}", file=sys.stderr)

    version = to_tag.lstrip("v")
    output_path = Path(args.output or f"RELEASE_NOTES_{version}.md")
    cache_path = Path(f"RELEASE_DATA_{version}.json")

    use_cache = cache_path.exists() and not args.no_cache

    if use_cache:
        data = load_cache(cache_path)
        tag = data["tag"]
        from_tag = data["from_tag"]
        repo = data["repo"]
        release_date = data["release_date"]
        release_body = data["release_body"]
        commits = data["commits"]
        milestone_items = data["milestone_items"]
        print(
            f"  {len(commits)} commits, "
            f"{'no' if milestone_items is None else len(milestone_items)} milestone items",
            file=sys.stderr,
        )
    else:
        if not from_tag:
            parser.error(
                "--from-tag is required when no cache file exists (or with --no-cache)"
            )

        tag = to_tag
        repo = args.repo

        print(f"Fetching release info for {tag}...", file=sys.stderr)
        release_body = get_release_body(tag, repo)

        release_date = args.release_date
        if not release_date:
            raw = gh(
                "release",
                "view",
                tag,
                "--repo",
                repo,
                "--json",
                "publishedAt",
                "--jq",
                ".publishedAt[:10]",
            )
            release_date = raw.strip()

        print(f"Fetching commits {from_tag}...{tag}...", file=sys.stderr)
        commits = get_commits(from_tag, tag, repo)
        print(f"  {len(commits)} commits found", file=sys.stderr)

        print("Resolving missing authors...", file=sys.stderr)
        commits = resolve_null_authors(commits, repo)

        commits = filter_commits(commits)
        print(f"  {len(commits)} commits after filtering", file=sys.stderr)

        milestone_items = None
        if args.milestone:
            print(f"Fetching open milestone {args.milestone} items...", file=sys.stderr)
            milestone_items = get_milestone_open_items(args.milestone, repo)
            print(f"  {len(milestone_items)} open items found", file=sys.stderr)

        save_cache(
            cache_path,
            tag,
            from_tag,
            repo,
            release_date,
            release_body,
            commits,
            milestone_items,
        )

    if args.dump_only:
        dump_raw(release_body, commits, tag, milestone_items)
        return

    notes = generate_notes(release_body, commits, tag, repo, release_date, args.model)

    if milestone_items is not None:
        notes += format_milestone_section(milestone_items, repo)

    output_path.write_text(notes, encoding="utf-8")
    print(f"Written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
