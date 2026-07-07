import pytest
from dotenv import load_dotenv
from agent.tools.github_tools import (
    parse_pr_url,
    get_pr_context,
    get_pr_diff,
    post_pr_comment
)

load_dotenv()

# ── Unit tests — no API calls ──────────────────────────
def test_parse_pr_url_valid():
    owner, repo, number = parse_pr_url(
        "https://github.com/mona/my-project/pull/5"
    )
    assert owner == "mona"
    assert repo == "my-project"
    assert number == 5

def test_parse_pr_url_trailing_slash():
    owner, repo, number = parse_pr_url(
        "https://github.com/mona/my-project/pull/5/"
    )
    assert number == 5

def test_parse_pr_url_invalid():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/mona/my-project")

# ── Integration tests — real API calls ─────────────────
# Replace with a real public PR URL you have access to
REAL_PR_URL = "https://github.com/yourname/mr-review-agent/pull/1"

def test_get_pr_context():
    context = get_pr_context(REAL_PR_URL)
    assert "title" in context
    assert "author" in context
    assert "base_branch" in context
    print(f"\nPR title: {context['title']}")
    print(f"Author: {context['author']}")

def test_get_pr_diff():
    diff = get_pr_diff(REAL_PR_URL)
    assert len(diff) > 0
    print(f"\nDiff length: {len(diff)} chars")
    print(f"First 200 chars:\n{diff[:200]}")