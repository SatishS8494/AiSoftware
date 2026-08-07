import re

_PROSE_PREFIX_RE = re.compile(
    r"^\s*(based on|here(?:'s| is)|sure[,!.]|okay[,!.]|of course|below is|the (?:fixed|corrected|updated)|i(?:'| a)ve|let me).*?\n",
    re.IGNORECASE,
)


def strip_code_fences(text: str) -> str:
    text = text.strip()

    fence_match = re.search(r"```[a-zA-Z0-9_-]*\s*\n(.*?)\n```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip("\n")

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        return text.strip("\n")

    text = _PROSE_PREFIX_RE.sub("", text, count=1)
    return text.strip("\n")
