#!/bin/bash
set -e

echo "🤖 MR Review Agent starting..."
echo "Checking environment..."

# Debug — verify keys are present (don't print the actual values)
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY is not set"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN is not set"
    exit 1
fi

echo "✅ Environment looks good"

PR_URL="https://github.com/$GITHUB_REPOSITORY/pull/$PR_NUMBER"
echo "📋 Reviewing PR: $PR_URL"

python -m agent.main "$PR_URL"