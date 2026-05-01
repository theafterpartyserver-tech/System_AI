# core/executor.py
from typing import Dict, Any, Optional
from pathlib import Path
import time

# New helpers:
from core.schema_validator import validate_tool_call
from core.trace import trace_event, log_event, log_performance
from core.tool_registry import ToolRegistry


class Executor:
    def __init__(
        self,
        cache_path: Path,
        memory_path: Path,
        events_log_path: Path,
        *,
        tool_registry: Optional[ToolRegistry] = None,
    ):
        self.cache_path = cache_path
        self.memory_path = memory_path
        self.events_log_path = events_log_path
        self.tool_registry = tool_registry

    def execute_tool(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.time()
        trace_event(
            "executor.incoming",
            metadata={"tool": tool_name},
            input_data=args,
        )

        registry = self.tool_registry
        if registry is None:
            result = {
                "status": "error",
                "tool": tool_name,
                "error": "No tool registry available",
            }
            log_event(
                trace_event(
                    "executor.missing_registry",
                    metadata={"tool": tool_name},
                    input_data=args,
                    output_data=result,
                )
            )
            return result

        # 1. Schema validation
        is_valid, reason = validate_tool_call(tool_name, args, registry._tools)

        if not is_valid:
            error_result = {
                "status": "error",
                "tool": tool_name,
                "error": f"schema_validation: {reason}",
                "raw_args": args,
            }
            log_event(
                trace_event(
                    "executor.validation_failed",
                    metadata={"tool": tool_name, "reason": reason},
                    input_data=args,
                    output_data=error_result,
                )
            )
            return error_result

        # 2. Tool existence and call
        tool_entry = registry.get_tool(tool_name)
        if tool_entry is None:
            result = {
                "status": "error",
                "tool": tool_name,
                "error": f"Unknown tool: {tool_name}",
            }
            log_event(
                trace_event(
                    "executor.tool_not_found",
                    metadata={"tool": tool_name},
                    input_data=args,
                    output_data=result,
                )
            )
            return result

        try:
            fn = tool_entry["function"]
            inner_start = time.time()
            result = fn(**args)

            log_performance(
                "executor.tool_call",
                inner_start,
                metadata={"tool": tool_name},
            )

            ok_result = {
                "status": "ok",
                "tool": tool_name,
                "result": result,
            }
            log_event(
                trace_event(
                    "executor.tool_success",
                    metadata={"tool": tool_name},
                    input_data=args,
                    output_data=ok_result,
                )
            )

            return ok_result

        except Exception as e:
            error_result = {
                "status": "error",
                "tool": tool_name,
                "error": str(e),
            }
            log_event(
                trace_event(
                    "executor.tool_error",
                    metadata={"tool": tool_name, "exception": type(e).__name__},
                    input_data=args,
                    output_data=error_result,
                )
            )
            return error_result
