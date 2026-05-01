from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


# ── Models ────────────────────────────────────────────────────────────────────

class RouteMode(str, Enum):
    CHAT = "chat"
    TOOL = "tool"
    FALLBACK = "fallback"
    SAFE = "safe"
    ELEVATED = "elevated"
    UNKNOWN = "unknown"


class RoutingStrategy(str, Enum):
    RULE_BASED = "rule_based"
    LLM_BASED = "llm_based"
    HYBRID = "hybrid"
    FAST_PATH = "fast_path"
    MULTI_STAGE = "multi_stage"
    CAPABILITY = "capability"
    FALLBACK = "fallback"


@dataclass
class RouteCandidate:
    name: str
    mode: RouteMode = RouteMode.UNKNOWN
    confidence: float = 0.0
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteDecision:
    strategy: RoutingStrategy
    selected: Optional[RouteCandidate] = None
    candidates: List[RouteCandidate] = field(default_factory=list)
    fallback_used: bool = False
    route_by_model_capability: bool = False
    timestamp: float = field(default_factory=time.time)
    debug: Dict[str, Any] = field(default_factory=dict)


# ── Policy ────────────────────────────────────────────────────────────────────

@dataclass
class RoutePolicy:
    allow_chat: bool = True
    allow_tool: bool = True
    allow_safe_tools: bool = True
    allow_elevated_tools: bool = True
    allow_fallback: bool = True
    min_confidence: float = 0.5


class RoutingPolicyEngine:
    def __init__(self, policy: Optional[RoutePolicy] = None):
        self.policy = policy or RoutePolicy()

    def approve(self, decision: RouteDecision) -> RouteDecision:
        if decision.selected is None:
            return decision
        if decision.selected.mode == RouteMode.CHAT and not self.policy.allow_chat:
            return self._reject(decision, "chat_not_allowed")
        if decision.selected.mode == RouteMode.TOOL and not self.policy.allow_tool:
            return self._reject(decision, "tool_not_allowed")
        if decision.selected.confidence < self.policy.min_confidence:
            return self._reject(decision, "low_confidence")
        return decision

    def _reject(self, decision: RouteDecision, reason: str) -> RouteDecision:
        decision.debug["policy_rejection"] = reason
        decision.selected = RouteCandidate(
            name="chat", mode=RouteMode.FALLBACK, confidence=0.0, reason=reason,
        )
        decision.fallback_used = True
        return decision


# ── Engine ────────────────────────────────────────────────────────────────────

class RoutingEngine:
    def __init__(self, registry: Any, memory_manager: Optional[Any] = None):
        self.registry = registry
        self.memory_manager = memory_manager
        self._route_cache: Dict[str, RouteDecision] = {}
        self._route_history: List[RouteDecision] = []
        self._strategy = RoutingStrategy.HYBRID

    def route(self, user_input: str, mode: str = "auto") -> RouteDecision:
        cache_key = self._cache_key(user_input, mode)
        if cache_key in self._route_cache:
            decision = self._route_cache[cache_key]
            self._route_history.append(decision)
            return decision
        decision = self._route_with_strategy(user_input, mode)
        self._route_cache[cache_key] = decision
        self._route_history.append(decision)
        return decision

    def _route_with_strategy(self, user_input: str, mode: str) -> RouteDecision:
        if mode == "chat_only":
            return self._chat_only_route(user_input)
        if mode == "tool_only":
            return self._tool_only_route(user_input)
        rule_candidate = self._rule_based_route(user_input)
        if rule_candidate:
            return RouteDecision(strategy=RoutingStrategy.HYBRID, selected=rule_candidate,
                                 candidates=[rule_candidate], debug={"source": "rule_based"})
        llm_candidate = self._llm_based_route(user_input)
        if llm_candidate:
            return RouteDecision(strategy=RoutingStrategy.HYBRID, selected=llm_candidate,
                                 candidates=[llm_candidate], debug={"source": "llm_based"})
        return self._fallback_route(user_input)

    def _chat_only_route(self, user_input: str) -> RouteDecision:
        c = RouteCandidate(name="chat", mode=RouteMode.CHAT, confidence=1.0,
                           reason="Forced chat-only mode.")
        return RouteDecision(strategy=RoutingStrategy.FAST_PATH, selected=c, candidates=[c])

    def _tool_only_route(self, user_input: str) -> RouteDecision:
        c = self._rule_based_route(user_input)
        if c:
            return RouteDecision(strategy=RoutingStrategy.RULE_BASED, selected=c,
                                 candidates=[c], debug={"forced": "tool_only"})
        return self._fallback_route(user_input)

    def _rule_based_route(self, user_input: str) -> Optional[RouteCandidate]:
        text = user_input.lower().strip()
        if self._looks_like_chat(text):
            return RouteCandidate(name="chat", mode=RouteMode.CHAT, confidence=0.95,
                                  reason="Matched chat fast-path rules.")
        tool_name = self._detect_tool_intent(text)
        if tool_name:
            return RouteCandidate(name=tool_name, mode=RouteMode.TOOL, confidence=0.9,
                                  reason="Matched tool intent rules.")
        return None

    def _llm_based_route(self, user_input: str) -> Optional[RouteCandidate]:
        return None

    def _fallback_route(self, user_input: str) -> RouteDecision:
        c = RouteCandidate(name="chat", mode=RouteMode.FALLBACK, confidence=0.3,
                           reason="Fallback to chat due to low confidence.")
        return RouteDecision(strategy=RoutingStrategy.FALLBACK, selected=c, candidates=[c],
                             fallback_used=True, debug={"reason": "no_route_match"})

    def _looks_like_chat(self, text: str) -> bool:
        return any(m in text for m in ["what is", "tell me", "explain", "why", "how", "who", "when"])

    def _detect_tool_intent(self, text: str) -> Optional[str]:
        if any(w in text for w in ["read", "open", "show", "view"]): return "file_read"
        if any(w in text for w in ["write", "save", "create file", "make file"]): return "file_write"
        if any(w in text for w in ["lint", "analyze code", "check code"]): return "lint_code"
        if any(w in text for w in ["generate", "code", "function"]): return "codegen"
        if any(w in text for w in ["shell", "command", "run"]): return "shell_exec"
        return None

    def _cache_key(self, user_input: str, mode: str) -> str:
        return f"{mode}:{user_input.strip().lower()}"

    def get_history(self) -> List[RouteDecision]: return list(self._route_history)
    def clear_cache(self) -> None: self._route_cache.clear()
    def set_strategy(self, strategy: RoutingStrategy) -> None: self._strategy = strategy
