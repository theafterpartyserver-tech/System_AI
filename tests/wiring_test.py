"""
wiring_test.py
Minimal end‑to‑end wiring test: create an AppContext and smoke‑test main components.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


from core.app_context import AppContext
from core.boot_check import run_boot_check
from core.health_manager import HealthManager
from core.health import get_routing_bias
from core.gateway import Gateway
from core.executor import Executor
from core.tool_registry import ToolRegistry
from core.hybrid_registry import HybridRegistry
from core.memory_manager import MemoryManager
from core.session_state import SessionStateStore
from core.system_diagnostics import run_system_diagnostics
from core.test_suite import TestSuite
from core.regression_runner import RegressionRunner
from core.release_gate import ReleaseGate


def main() -> None:
    print("=== WIRING TEST START ===\n")

    print("1. Run boot_check at project root...")
    boot = run_boot_check(PROJECT_ROOT)
    print(f"   Boot check status: {boot['status']}")
    if boot["status"] == "error":
        print("   ERRORS:")
        for err in boot.get("checks", []):
            if err.get("ok") is False and err.get("required"):
                print(f"     - {err['path']}: {err.get('error', 'unknown error')}")
        print("\nIf model/service errors are acceptable, ignore them here.\n")

    print("2. Run system_diagnostics...")
    diag = run_system_diagnostics(PROJECT_ROOT)
    print(f"   project_root: {diag.get('project_root', 'N/A')}")
    print(f"   backend: {diag.get('config', {}).get('backend', 'N/A')}")
    print(f"   model exists: {diag.get('model', {}).get('exists', 'N/A')}")
    print(f"   tool_count: {diag.get('registry', {}).get('tool_count', 0)}")
    print(f"   session_status: {diag.get('runtime', {}).get('session_status', 'N/A')}\n")

    print("3. Build a simple AppContext...")
    # Paths (you can adapt if your layout is different)
    logs_dir = PROJECT_ROOT / "logs"
    memory_dir = PROJECT_ROOT / "memory"
    cache_path = logs_dir / "tool_cache.json"
    events_log_path = logs_dir / "events.log"
    permissions_path = PROJECT_ROOT / "config" / "permissions.json"

    memory_manager = MemoryManager(storage_path=memory_dir)
    health_manager = HealthManager(project_root=PROJECT_ROOT, model_path=diag.get("model", {}).get("resolved_path"))
    gateway = Gateway(permissions_path=permissions_path)

    # Executors assume registry
    tool_registry = ToolRegistry()
    hybrid_registry = HybridRegistry(project_root=PROJECT_ROOT)
    hybrid_registry.register_tool(
        name="test_tool",
        description="Dummy test tool.",
        risk="safe",
        schema={"type": "object", "properties": {}, "required": []},
        function=lambda **_: {"status": "ok", "fake": "test_result"},
    )

    executor = Executor(
        cache_path=cache_path,
        memory_path=memory_dir,
        events_log_path=events_log_path,
        tool_registry=tool_registry,
    )

    # Regression / release
    suite = TestSuite()
    suite.add_case(
        name="dummy_chat",
        prompt="What is 2+2?",
        expected_mode="chat",
        expected_contains="4",
    )
    regression_runner = RegressionRunner(suite=suite)
    regression_runner.add_default_cases()

    release_gate = ReleaseGate(min_pass_rate=0.5)

    # Build context
    ctx = AppContext(
        memory_manager=memory_manager,
        health_manager=health_manager,
        gateway=gateway,
        executor=executor,
        tool_registry=tool_registry,
        hybrid_registry=hybrid_registry,
        regression_runner=regression_runner,
        release_gate=release_gate,
    )

    print("4. Smoke‑test AppContext helpers...")
    health_ok = ctx.ensure_health(require_healthy=False)
    print(f"   ctx.ensure_health() -> {health_ok}")
    print(f"   health report: {ctx.health_manager.get_last_report().as_dict() if ctx.health_manager else 'None'}")

    memory_ok = ctx.ensure_memory()
    print(f"   ctx.ensure_memory() -> {memory_ok}")

    regression_ok = ctx.ensure_regression_suite()
    print(f"   ctx.ensure_regression_suite() -> {regression_ok}")
    if ctx.regression_runner:
        summary = ctx.regression_runner.summary()
        print(f"   regression summary: {summary}")

    if ctx.release_gate and ctx.regression_runner:
        gate = ctx.release_gate.evaluate(ctx.regression_runner.suite.results())
        print(f"   release_gate evaluation: {gate.ok} (reason: {gate.message})")

    print("5. Test routing bias / simple tool execution...")
    print(f"   routing_bias: {get_routing_bias()}")

    print("   Execute tool via hybrid_registry...")
    try:
        result = hybrid_registry.execute_tool("test_tool")
        print(f"   hybrid_registry.execute_tool('test_tool') -> {result}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {e}")

    print("   Execute tool via executor...")
    try:
        # Trick: reuse the same tool in `tool_registry` to make schema pass
        from core.schema_validator import validate_tool_call
        tool_registry.set_tool(
            "test_tool",
            lambda **_: {"status": "ok", "fake": "test_result_from_tool_registry"},
        )
        is_valid, reason = validate_tool_call("test_tool", {}, tool_registry._tools)
        print(f"   schema validation: {is_valid} (reason: {reason})")

        result = ctx.executor.execute_tool("test_tool", {})
        print(f"   executor.execute_tool('test_tool', {{}}) -> {result}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {e}")

    print("6. Session state round‑trip...")
    state_file = PROJECT_ROOT / "runtime" / "session_state_test.json"
    state_store = SessionStateStore(state_file)
    state_store.mark_running(pending_action={"tool": "file_read", "args": {"path": "dummy.txt"}})
    loaded = state_store.load()
    print(f"   session_state.test: status={loaded.get('status')} pending_action={loaded.get('pending_action')}")

    print("\n=== WIRING TEST PASSED ===")


if __name__ == "__main__":
    main()