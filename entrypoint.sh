#!/bin/bash
set -e

echo "🤖 MR Review Agent starting..."

# GitHub Actions provides these automatically
PR_URL="https://github.com/$GITHUB_REPOSITORY/pull/$PR_NUMBER"

echo "📋 Reviewing PR: $PR_URL"

python -m agent.main "$PR_URL"