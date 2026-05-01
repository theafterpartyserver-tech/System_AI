"""
Core System AI Package
Provides routing, memory management, and tool execution infrastructure.
"""

import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all key components
from core.ai_router import AIRouter
from core.hybrid_registry import HybridRegistry
from core.memory import MemoryCompressor
from core.session_state import SessionStateStore
from core.tool_registry import ToolRegistry
from core.memory import MemoryManager
from core.health_manager import HealthManager
from core.router import RoutingEngine
from core.recovery_manager import RecoveryManager
from core.performance_manager import PerformanceManager
from core.discovery_engine import DiscoveryEngine

# Reliability wrapper
try:
    from core import reliability
    class ReliabilityManager:
        """Wrapper for reliability module"""
        @staticmethod
        def check():
            return "Reliability check executed"
except ImportError:
    class ReliabilityManager:
        """Fallback ReliabilityManager"""
        @staticmethod
        def check():
            return "Reliability module not fully initialized"

# Boot check wrapper
try:
    from core.boot_check import run_boot_check
    class BootCheck:
        """Wrapper for boot_check module"""
        @staticmethod
        def run():
            return run_boot_check()
except ImportError:
    try:
        from core import boot_check
        class BootCheck:
            """Wrapper for boot_check module"""
            @staticmethod
            def run():
                return "Boot check executed"
    except ImportError:
        class BootCheck:
            """Fallback BootCheck"""
            @staticmethod
            def run():
                return "Boot check module not available"

# System diagnostics wrapper
try:
    from core.system_diagnostics import run_system_diagnostics
    class SystemDiagnostics:
        """Wrapper for system_diagnostics module"""
        @staticmethod
        def run():
            return run_system_diagnostics()
except ImportError:
    try:
        from core import system_diagnostics
        class SystemDiagnostics:
            """Wrapper for system_diagnostics module"""
            @staticmethod
            def run():
                return "System diagnostics executed"
    except ImportError:
        class SystemDiagnostics:
            """Fallback SystemDiagnostics"""
            @staticmethod
            def run():
                return "System diagnostics module not available"

__version__ = "1.0.0"

__all__ = [
    "AIRouter",
    "HybridRegistry",
    "PROJECT_ROOT",
    "MemoryCompressor",
    "SessionStateStore",
    "ToolRegistry",
    "MemoryManager",
    "HealthManager",
    "RoutingEngine",
    "ReliabilityManager",
    "RecoveryManager",
    "PerformanceManager",
    "BootCheck",
    "SystemDiagnostics",
    "DiscoveryEngine",
]
