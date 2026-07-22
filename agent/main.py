import sys
from agent.agent import create_agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m agent.main <PR_URL>")
        print("Example: python -m agent.main https://github.com/owner/repo/pull/5")
        sys.exit(1)

    pr_url = sys.argv[1]

    print(f"\n🤖 MR Review Agent starting...")
    print(f"📋 PR: {pr_url}\n")

    agent = create_agent()

    result = agent.invoke({
        "input": f"Review this GitHub Pull Request: {pr_url}"
    })

    print(f"\n✅ {result.get('output', 'Review completed')}")

if __name__ == "__main__":
    main()