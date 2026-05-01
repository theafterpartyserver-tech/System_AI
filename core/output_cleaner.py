from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass
class CleanedOutput:
    original: str
    cleaned: str
    removed_fragments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OutputCleaner:
    def __init__(self):
        self._strip_markers = [
            "User:",
            "Assistant:",
            "Response:",
            "Input:",
            "Question:",
        ]

    def clean(self, text: str, max_lines: int = 4) -> CleanedOutput:
        original = text or ""
        cleaned = original
        removed: List[str] = []

        cleaned, fragments = self.strip_prompt_fragments(cleaned)
        removed.extend(fragments)

        cleaned, fragments = self.strip_tool_markers(cleaned)
        removed.extend(fragments)

        cleaned = self.collapse_repeated_lines(cleaned)
        cleaned = self.collapse_repeated_tokens(cleaned)
        cleaned = self.trim_to_max_lines(cleaned, max_lines=max_lines)
        cleaned = self.normalize_whitespace(cleaned)
        cleaned = self.strip_terminal_punctuation_noise(cleaned)

        return CleanedOutput(
            original=original,
            cleaned=cleaned,
            removed_fragments=removed,
            metadata={
                "max_lines": max_lines,
                "removed_count": len(removed),
            },
        )

    def strip_prompt_fragments(self, text: str) -> tuple[str, List[str]]:
        removed: List[str] = []
        if not text:
            return text, removed

        for marker in self._strip_markers:
            idx = text.find(marker)
            if idx != -1:
                removed.append(text[idx:])
                text = text[:idx]
        return text.strip(), removed

    def strip_tool_markers(self, text: str) -> tuple[str, List[str]]:
        removed: List[str] = []
        if not text:
            return text, removed

        patterns = [
            r"\blint_code\b",
            r"\bcodegen\b",
            r"\bfile_read\b",
            r"\bfile_write\b",
            r"\bshell_exec\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                removed.append(text[match.start():])
                text = text[:match.start()]
        return text.strip(), removed

    def collapse_repeated_lines(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""

        deduped = []
        for line in lines:
            if not deduped or line != deduped[-1]:
                deduped.append(line)

        if len(deduped) > 1 and all(line == deduped[0] for line in deduped):
            return deduped[0]

        return "\n".join(deduped)

    def collapse_repeated_tokens(self, text: str) -> str:
        if not text:
            return text

        tokens = text.split()
        if len(tokens) < 6:
            return text.strip()

        compressed = [tokens[0]]
        run_count = 1
        for token in tokens[1:]:
            if token == compressed[-1]:
                run_count += 1
                if run_count <= 2:
                    compressed.append(token)
            else:
                run_count = 1
                compressed.append(token)

        return " ".join(compressed).strip()

    def trim_to_max_lines(self, text: str, max_lines: int = 4) -> str:
        if not text:
            return text
        lines = text.splitlines()
        if len(lines) <= max_lines:
            return text.strip()
        return "\n".join(lines[:max_lines]).strip()

    def normalize_whitespace(self, text: str) -> str:
        if not text:
            return text
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    def strip_terminal_punctuation_noise(self, text: str) -> str:
        if not text:
            return text
        return text.strip().replace("..", ".").replace("??", "?").replace("!!", "!")
