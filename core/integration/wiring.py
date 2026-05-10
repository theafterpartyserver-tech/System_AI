from __future__ import annotations

from typing import Any, Dict, Optional
import json
from pathlib import Path

from core.app_context import AppContext
from core.memory import MemoryManager
from core.output_cleaner import OutputCleaner
from core.router import RoutingEngine, RouteMode
from core.gateway import Gateway
from core.ai_router import AIRouter


# The unified wiring layer that orchestrates everything
class IntegratedRouter:
    """
    Complete integration layer that wraps AIRouter behavior.
    Handles: recovery, health, memory, routing, permissions, output cleaning, validation.
    This is the unified entry point for ALL user input.
    """
    
    def __init__(self, context: AppContext) -> None:
        self.context = context
        # FIX: Use absolute path relative to project root
        PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
        config_path = PROJECT_ROOT / "config" / "config.json"
        self.router = AIRouter(context.registry, config_path)
        
        # Initialize gateway from permissions config
        permissions_path = PROJECT_ROOT / "config" / "permissions.json"
        self.gateway = Gateway(permissions_path) if permissions_path.exists() else None

    def parse_intent(self, user_input: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Main entry point: processes user input through COMPLETE system.
        
        Flow:
        1. Health check + recovery snapshot
        2. Memory logging (session)
        3. Routing decision (hybrid)
        4. Permission gateway check
        5. Tool execution (if applicable)
        6. Output validation + cleaning
        7. Memory persistence
        8. Recovery hint generation
        """
        
        # ========== STEP 1: HEALTH + RECOVERY ==========
        if self.context.recovery_manager:
            snapshot = self.context.recovery_manager.create_snapshot(
                session_id="default",
                last_user_input=user_input,
            )

        if self.context.health_manager:
            # Check for timeout recovery before processing
            self.context.health_manager.check_timeout_recovery()
            self.context.health_manager.log_session_event(
                "parse_intent_start", 
                {"user_input": user_input}
            )

        # ========== STEP 2: MEMORY LOGGING ==========
        if self.context.memory_manager:
            self.context.memory_manager.add_session(
                user_input, 
                memory_type="user_input"
            )

        # ========== STEP 3: ROUTING DECISION ==========
        result = None
        if self.context.routing_engine:
            decision = self.context.routing_engine.route(user_input, mode)
            
            # Build result based on routing decision
            if decision.selected:
                if decision.selected.mode == RouteMode.CHAT:
                    result = self._build_chat_result(user_input)
                elif decision.selected.mode == RouteMode.TOOL:
                    result = self._build_tool_result(
                        user_input, 
                        decision.selected.name
                    )

        # Fallback if routing failed
        if result is None:
            result = self.router.parse_intent(user_input, mode)

        # ========== STEP 4: PERMISSION GATEWAY ==========
        if result.get("tool") and self.gateway:
            gateway_check = self.gateway.check_tool(result["tool"], user_mode="user")
            result["_gateway_decision"] = gateway_check
            
            if gateway_check["decision"] == "DENY":
                result["status"] = "denied"
                result["reason"] = gateway_check["reason"]
                return result

        # ========== STEP 5: MEMORY UPDATE (routing) ==========
        if self.context.memory_manager:
            if result.get("tool"):
                self.context.memory_manager.add_session(
                    f"Tool routing: {result['tool']}",
                    memory_type="routing_decision",
                    tool_usage=result["tool"],
                )
            else:
                self.context.memory_manager.add_session(
                    "Chat mode routing",
                    memory_type="routing_decision",
                )

        # ========== STEP 6: OUTPUT CLEANUP ==========
        if self.context.output_cleaner:
            raw_response = result.get("raw_response", "")
            cleaned = self.context.output_cleaner.clean(raw_response)
            result["cleaned_response"] = cleaned.cleaned
            result["removed_fragments"] = cleaned.removed_fragments

        # ========== STEP 7: MEMORY PERSISTENCE ==========
        if self.context.memory_manager:
            response_text = result.get("cleaned_response", result.get("raw_response", ""))
            
            if result.get("tool"):
                self.context.memory_manager.add_session(
                    response_text,
                    memory_type="tool_result",
                    tool_usage=result["tool"],
                )
            else:
                self.context.memory_manager.add_session(
                    response_text,
                    memory_type="chat_response",
                )

        # ========== STEP 8: PERFORMANCE TRACKING ==========
        if self.context.performance_manager:
            # Record that this operation completed
            pass

        # ========== STEP 9: HEALTH LOGGING ==========
        if self.context.health_manager:
            self.context.health_manager.log_session_event(
                "parse_intent_complete",
                {
                    "user_input": user_input,
                    "mode": result.get("mode"),
                    "tool": result.get("tool"),
                }
            )

        # ========== STEP 10: RECOVERY HINT ==========
        if self.context.recovery_manager and self._looks_like_failure(result):
            prompt_builder = self.context.recovery_prompt_builder
            if prompt_builder:
                recovery_prompt = prompt_builder.build_after_failure(
                    "weak_routing", 
                    last_user_input=user_input
                )
                if self.context.memory_manager:
                    self.context.memory_manager.add_session(
                        recovery_prompt.prompt_text, 
                        memory_type="recovery_hint"
                    )

        return result

    def _build_chat_result(self, text: str) -> Dict[str, Any]:
        """Build a chat mode result."""
        return {
            "mode": "chat",
            "intent": "",
            "tool": None,
            "args": {},
            "raw_response": text,
            "status": "success",
        }

    def _build_tool_result(self, text: str, tool_name: str) -> Dict[str, Any]:
        """Build a tool execution result."""
        return {
            "mode": "tool",
            "intent": f"tool_{tool_name}",
            "tool": tool_name,
            "args": {"prompt": text},
            "raw_response": "",
            "status": "pending",
        }

    def _looks_like_failure(self, result: Dict[str, Any]) -> bool:
        """Detect if result indicates a failure."""
        mode = result.get("mode")
        status = result.get("status")
        response = result.get("raw_response", "")
        
        # Failure indicators
        if status in ("error", "denied", "failed"):
            return True
        
        if mode in (None, "chat") and response == "":
            return True
        
        return False
