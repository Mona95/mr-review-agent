import os
from github import Github
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set in environment")
    return Github(token)

def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    """
    Parse a Github PR URL into (owner, repo, pr_number)

    Example:
    https://github.com/mona/my-project/pull/5
    -> ("mona", "my-project", 5)
    """

    # remove trailing stash if present
    pr_url = pr_url.rstrip("/")

    parts = pr_url.split("/")

    # validate URL format
    if "github.com" not in pr_url or "pull" not in parts:
        raise ValueError(
            f"Invalid GitHub PR URL: {pr_url}\n"
            f"Expected format: https://github.com/owner/repo/pull/123"
        )

    try:
        pull_index = parts.index("pull")
        owner = parts[pull_index - 2]
        repo = parts[pull_index - 1]
        pr_number = int(parts[pull_index + 1])
        return owner, repo, pr_number
    except (ValueError, IndexError):
        raise ValueError(f"Could not parse PR URL: {pr_url}")


def get_pr_context(pr_url: str) -> dict:
    """
    Fetch PR metadata — title, description, author, branch info.
    Gives the AI context about the intent of the change.
    """
    g = get_github_client()
    owner, repo_name, pr_number = parse_pr_url(pr_url)

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    return {
        "title": pr.title,
        "description": pr.body or "No description provided",
        "author": pr.user.login,
        "base_branch": pr.base.ref,      # target branch e.g. "main"
        "head_branch": pr.head.ref,      # source branch e.g. "feat/login"
        "changed_files": pr.changed_files,
        "additions": pr.additions,
        "deletions": pr.deletions,
        "state": pr.state,
        "url": pr_url
    }

def get_pr_diff(pr_url: str) -> str:
    """
    Fetch the full diff of a PR — all changed files and lines.
    Returns a formatted string the AI can read and analyze.
    """
    g = get_github_client()
    owner, repo_name, pr_number = parse_pr_url(pr_url)

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    files = pr.get_files()

    diff_text = ""
    total_files = 0

    for file in files:
        total_files += 1

        # Skip files that are too large or binary
        if file.patch is None:
            diff_text += f"\n### {file.filename} (binary or too large — skipped)\n"
            continue

        diff_text += f"""
### File: {file.filename}
Status: {file.status}  |  +{file.additions} additions  |  -{file.deletions} deletions

```diff
{file.patch}
```
"""

    if not diff_text:
        return "No changes found in this PR."

    summary = f"Total files changed: {total_files}\n\n"
    return summary + diff_text

def post_pr_comment(pr_url: str, comment: str) -> str:
    """
    Post a review comment on the PR.
    If a previous review comment from this bot exists — update it.
    """
    g = get_github_client()
    owner, repo_name, pr_number = parse_pr_url(pr_url)

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    bot_marker = "<!-- mr-review-agent -->"
    full_comment = f"{bot_marker}\n{comment}"

    # Check if bot already commented — update instead of creating new
    existing_comments = pr.get_issue_comments()
    for existing in existing_comments:
        if bot_marker in existing.body:
            existing.edit(full_comment)
            return f"✅ Review comment updated on PR #{pr_number}"

    # No existing comment — create new one
    pr.create_issue_comment(full_comment)
    return f"✅ Review comment posted on PR #{pr_number}"