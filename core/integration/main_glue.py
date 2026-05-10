from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from core.app_context import AppContext
from core.health_manager import HealthManager
from core.memory import MemoryManager
from core.router import RoutingEngine
from core.router import RoutingPolicyEngine
from core.recovery_manager import RecoveryManager
from core.output_cleaner import OutputCleaner
from core.performance_manager import PerformanceManager, PerformanceConfig
from core.regression_runner import RegressionRunner
from core.recovery_prompting import RecoveryPromptBuilder
from core.hybrid_registry import HybridRegistry
from core.release_gate import ReleaseGate


def setup_context(
    registry: HybridRegistry,
    config_path: Path,
    model_path: Optional[Path] = None,
    state_dir: Optional[Path] = None,
) -> AppContext:
    """
    Initialize AppContext with all core managers.
    This is the canonical wiring point for the entire system.
    """
    # Initialize all managers
    project_root = config_path.parent if config_path else Path.cwd()
    health = HealthManager(model_path=model_path, project_root=project_root)
    memory = MemoryManager(storage_path=state_dir)
    routing = RoutingEngine(registry=registry, memory_manager=memory)
    policy = RoutingPolicyEngine()
    recovery = RecoveryManager(state_dir=state_dir)
    output_cleaner = OutputCleaner()
    
    perf = PerformanceManager(
        config=PerformanceConfig(
            max_context_length=4096,
            max_chat_tokens=256,
            max_tool_tokens=256,
            inference_timeout_seconds=20.0,
        )
    )
    
    regression = RegressionRunner()
    regression.add_default_cases()
    
    release_gate = ReleaseGate()

    # Create context with all managers
    context = AppContext(
        memory_manager=memory,
        health_manager=health,
        routing_engine=routing,
        routing_policy=policy,
        recovery_manager=recovery,
        performance_manager=perf,
    )
    
    # Attach additional managers
    context.regression_runner = regression
    context.output_cleaner = output_cleaner
    context.recovery_prompt_builder = RecoveryPromptBuilder()
    context.release_gate = release_gate
    context.registry = registry

    # Run startup checks
    print("\n[STARTUP] Running health checks...")
    health_ok = context.ensure_health(require_healthy=False)
    
    print("[STARTUP] Checking memory system...")
    memory_ok = context.ensure_memory()
    
    print("[STARTUP] Running regression suite...")
    test_ok = context.ensure_regression_suite()

    context.health_ok = health_ok
    context.memory_ok = memory_ok
    context.test_ok = test_ok

    # Report startup status
    print("\n[STARTUP] System initialization report:")
    print(f"  Health checks: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"  Memory system: {'✓ PASS' if memory_ok else '✗ FAIL'}")
    print(f"  Regression suite: {'✓ PASS' if test_ok else '✗ FAIL'}")
    
    if health_ok and memory_ok and test_ok:
        print("\n[STARTUP] ✓ All systems operational. Ready for interaction.")
    else:
        print("\n[STARTUP] ⚠ Warning: Some systems degraded. Proceeding with caution.")

    return context
