def format_review(feedback: dict, pr_url: str) -> str:
    score = feedback.get("score", 0)
    summary = feedback.get("summary", "Review complete")
    categories = feedback.get("categories", {})
    positives = feedback.get("positives", [])

    # Score emoji
    if score >= 80:
        score_emoji = "🟢"
    elif score >= 60:
        score_emoji = "🟡"
    else:
        score_emoji = "🔴"

    total_issues = sum(len(items) for items in categories.values())

    lines = [
        "## 🤖 AI Code Review",
        "",
        f"{score_emoji} **Score: {score}/100** · {total_issues} issue{'s' if total_issues != 1 else ''} found",
        "",
        f"> {summary}",
        "",
        "---",
        ""
    ]

    severity_config = {
        "critical": ("🔴", "Critical"),
        "high": ("🟠", "High"),
        "medium": ("🟡", "Medium"),
        "low": ("🔵", "Low")
    }

    category_config = {
        "security": "🔒 Security",
        "bugs": "🐛 Bugs",
        "performance": "⚡ Performance",
        "style": "✨ Style"
    }

    has_issues = False
    for category_key, category_label in category_config.items():
        items = categories.get(category_key, [])
        if not items:
            continue

        has_issues = True
        lines.append(f"### {category_label}")
        lines.append("")

        for item in items:
            severity = item.get("severity", "low")
            emoji, label = severity_config.get(severity, ("🔵", "Low"))

            lines.append(f"**{emoji} {label}** · `{item.get('file', 'unknown')}`")
            lines.append("")

            line_context = item.get("line_context", "")
            if line_context:
                lines.append("```")
                lines.append(line_context)
                lines.append("```")
                lines.append("")

            lines.append(f"**Issue:** {item.get('issue', '')}")
            lines.append("")
            lines.append(f"**Suggestion:** {item.get('suggestion', '')}")
            lines.append("")
            lines.append("---")
            lines.append("")

    if not has_issues:
        lines.append("### ✅ No issues found")
        lines.append("")
        lines.append("This looks clean. Great work.")
        lines.append("")
        lines.append("---")
        lines.append("")

    if positives:
        lines.append("### 👍 What looks good")
        lines.append("")
        for positive in positives:
            lines.append(f"- {positive}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(
        f"*Reviewed by [MR Review Agent](https://github.com/Mona95/mr-review-agent) "
        f"· Powered by Groq · llama-3.3-70b*"
    )

    return "\n".join(lines)