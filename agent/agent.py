import os
import json
from dotenv import load_dotenv
from groq import Groq

from agent.tools.github_tools import (
    get_pr_diff,
    get_pr_context,
    post_pr_comment
)
from agent.tools.review_tools import review_code
from agent.formatter import format_review

load_dotenv()

def create_agent():
    return MRReviewAgent()

class MRReviewAgent:
    """
    A simple agent that reviews GitHub PRs.
    Implements the ReAct pattern manually — no LangChain needed.
    """

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.tools = {
            "get_pr_diff": get_pr_diff,
            "get_pr_context": get_pr_context,
            "review_code": self._review_code_wrapper,
            "post_pr_comment": self._post_comment_wrapper
        }

    def invoke(self, input_dict: dict) -> dict:
        pr_url = input_dict.get("input", "").split()[-1]

        print("Thought: I need to get the PR diff first")
        diff = self._call_tool("get_pr_diff", pr_url)

        print("\nThought: Now I need the PR context")
        context = self._call_tool("get_pr_context", pr_url)

        print("\nThought: Now I will review the code")
        review_input = json.dumps({
            "diff": diff,
            "context": context
        })
        formatted_review = self._call_tool("review_code", review_input)

        print("\nThought: Now I will post the comment")
        comment_input = json.dumps({
            "pr_url": pr_url,
            "comment": formatted_review
        })
        result = self._call_tool("post_pr_comment", comment_input)

        print(f"\nThought: All steps complete")
        return {"output": result}

    def _call_tool(self, tool_name: str, tool_input: str) -> any:
        print(f"Action: {tool_name}")
        print(f"Action Input: {str(tool_input)[:100]}...")

        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: tool {tool_name} not found"

        result = tool(tool_input)
        print(f"Observation: {str(result)[:100]}...")
        return result

    def _review_code_wrapper(self, input_str: str) -> str:
        try:
            data = json.loads(input_str)
            diff = data.get("diff", "")
            context = data.get("context", {})
            feedback = review_code(diff, context)
            return format_review(feedback, context.get("url", ""))
        except Exception as e:
            return f"Error during review: {str(e)}"

    def _post_comment_wrapper(self, input_str: str) -> str:
        try:
            data = json.loads(input_str)
            pr_url = data.get("pr_url", "")
            comment = data.get("comment", "")
            return post_pr_comment(pr_url, comment)
        except Exception as e:
            return f"Error posting comment: {str(e)}"