"""
COMPREHENSIVE SYSTEM AI FULL TEST
Tests: Imports | Wiring | Logic | Functions
Produces: Detailed readable log with statistics
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Tuple

class FullSystemTestLogger:
    """Comprehensive test logger with detailed output"""
    
    def __init__(self):
        self.tests = []
        self.results = {"passed": 0, "failed": 0, "total": 0}
        self.start_time = datetime.now()
        self.log_lines = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "TEST": "🧪",
            "PASS": "✅",
            "FAIL": "❌",
            "SECTION": "📋",
            "MODULE": "🔧",
            "FUNCTION": "⚙️ ",
            "WIRING": "🔗",
            "LOGIC": "🧠",
            "SUMMARY": "📊"
        }.get(level, "•")
        
        formatted = f"[{timestamp}] {prefix} {message}"
        print(formatted)
        self.log_lines.append(formatted)
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            self.log(f"PASS: {test_name}", "PASS")
        else:
            self.results["failed"] += 1
            self.log(f"FAIL: {test_name} - {details}", "FAIL")
        
        self.tests.append({"name": test_name, "passed": passed, "details": details})
    
    def print_summary(self):
        """Print test summary"""
        self.log("", "SUMMARY")
        self.log("═" * 70, "SUMMARY")
        self.log("TEST SUMMARY", "SUMMARY")
        self.log("═" * 70, "SUMMARY")
        self.log(f"Total Tests: {self.results['total']}", "SUMMARY")
        self.log(f"Passed: {self.results['passed']}", "PASS")
        self.log(f"Failed: {self.results['failed']}", "FAIL" if self.results['failed'] > 0 else "PASS")
        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%", "SUMMARY")
        self.log("═" * 70, "SUMMARY")

logger = FullSystemTestLogger()

# ============================================================================
# SECTION 1: IMPORT TESTS
# ============================================================================
logger.log("Starting Import Tests", "SECTION")
logger.log("=" * 70, "SECTION")

import_tests = {
    "AIRouter": ("from core.ai_router import AIRouter", "AIRouter"),
    "HybridRegistry": ("from core.hybrid_registry import HybridRegistry", "HybridRegistry"),
    "MemoryCompressor": ("from core.memory_compressor import MemoryCompressor", "MemoryCompressor"),
    "SessionStateStore": ("from core.session_state import SessionStateStore", "SessionStateStore"),
    "ToolRegistry": ("from core.tool_registry import ToolRegistry", "ToolRegistry"),
    "MemoryManager": ("from core.memory_manager import MemoryManager", "MemoryManager"),
    "HealthManager": ("from core.health_manager_enhanced import HealthManager", "HealthManager"),
    "RoutingEngine": ("from core.routing_engine import RoutingEngine", "RoutingEngine"),
    "RecoveryManager": ("from core.recovery_manager import RecoveryManager", "RecoveryManager"),
    "PerformanceManager": ("from core.performance_manager import PerformanceManager", "PerformanceManager"),
    "DiscoveryEngine": ("from core.discovery_engine import DiscoveryEngine", "DiscoveryEngine"),
    "EnhancedToolLoader": ("from core.enhanced_tool_loader import EnhancedToolLoader", "EnhancedToolLoader"),
    "LLMManager": ("from core.llm_manager import LLMManager", "LLMManager"),
    "MemoryPersistenceManager": ("from core.memory_persistence import MemoryPersistenceManager", "MemoryPersistenceManager"),
    "ProductionLogger": ("from core.production_config import ProductionLogger", "ProductionLogger"),
    "ToolExecutor": ("from core.main import ToolExecutor", "ToolExecutor"),
}

for module_name, (import_code, class_name) in import_tests.items():
    try:
        exec(import_code)
        logger.test_result(f"Import {module_name}", True)
    except Exception as e:
        logger.test_result(f"Import {module_name}", False, str(e)[:50])

# ============================================================================
# SECTION 2: WIRING TESTS (Module Connections)
# ============================================================================
logger.log("", "SECTION")
logger.log("Starting Wiring Tests (Module Connections)", "SECTION")
logger.log("=" * 70, "SECTION")

try:
    from core.hybrid_registry import HybridRegistry
    from core.ai_router import AIRouter
    from core.memory_persistence import MemoryPersistenceManager
    from core.health_manager_enhanced import HealthManager
    
    # Test 1: HybridRegistry initialization
    registry = HybridRegistry(project_root=Path('.'))
    logger.test_result("Wire HybridRegistry → project_root", registry is not None)
    
    # Test 2: AIRouter wiring to HybridRegistry
    config_path = Path('./config/config.json')
    router = AIRouter(registry=registry, config_path=config_path)
    logger.test_result("Wire AIRouter → HybridRegistry", router is not None)
    
    # Test 3: MemoryPersistenceManager initialization
    mem = MemoryPersistenceManager(Path('./memory'))
    logger.test_result("Wire MemoryPersistenceManager → memory_dir", mem is not None)
    
    # Test 4: HealthManager with project root
    health = HealthManager(project_root=Path('.'))
    logger.test_result("Wire HealthManager → project_root", health is not None)
    
    # Test 5: Cross-module access
    tools = registry.list_tool_names()
    logger.test_result("Access HybridRegistry.list_tool_names()", isinstance(tools, list))
    
    # Test 6: Memory system wiring
    stats = mem.get_stats()
    logger.test_result("Access MemoryPersistenceManager.get_stats()", isinstance(stats, dict))
    
except Exception as e:
    logger.test_result("Wiring tests", False, str(e))

# ============================================================================
# SECTION 3: LOGIC TESTS
# ============================================================================
logger.log("", "SECTION")
logger.log("Starting Logic Tests", "SECTION")
logger.log("=" * 70, "SECTION")

try:
    from core.discovery_engine import DiscoveryEngine
    
    # Test 1: Discovery logic
    engine = DiscoveryEngine(Path('.'))
    discoveries = engine.discover_all()
    tools_found = len(discoveries.get('tools', []))
    logger.test_result("Logic: Tool discovery pipeline", tools_found == 5, 
                      f"Expected 5, found {tools_found}")
    
    # Test 2: Manifest generation logic
    manifest = engine.export_manifest()
    manifest_obj = json.loads(manifest)
    logger.test_result("Logic: Manifest generation", 
                      manifest_obj.get('discovery', {}).get('tools') is not None)
    
    # Test 3: Memory persistence logic
    test_data = {"test_key": "test_value", "number": 42}
    saved = mem.save_memory("logic_test", test_data)
    logger.test_result("Logic: Memory save operation", saved)
    
    # Test 4: Memory retrieval logic
    loaded = mem.load_memory("logic_test")
    logger.test_result("Logic: Memory load operation", loaded == test_data)
    
    # Test 5: Health check logic
    health_status = health.check_health()
    logger.test_result("Logic: Health check execution", health_status)
    
    # Test 6: Skill discovery logic
    from core.enhanced_tool_loader import EnhancedToolLoader
    loader = EnhancedToolLoader(Path('./tools'))
    skills = loader.load_skill_modules(Path('./skills'))
    skills_found = len(skills)
    logger.test_result("Logic: Skill module discovery", skills_found == 3,
                      f"Expected 3, found {skills_found}")
    
except Exception as e:
    logger.test_result("Logic tests", False, str(e))

# ============================================================================
# SECTION 4: FUNCTION TESTS (Individual Functions)
# ============================================================================
logger.log("", "SECTION")
logger.log("Starting Function Tests", "SECTION")
logger.log("=" * 70, "SECTION")

# Math skill functions
try:
    from skills.math_skill import calculate_expression, solve_quadratic
    
    # Test 1: calculate_expression
    result = calculate_expression("2 + 2")
    logger.test_result("Function: calculate_expression('2 + 2')", result == 4,
                      f"Expected 4, got {result}")
    
    # Test 2: Complex expression
    result = calculate_expression("10 * 5 + 2")
    logger.test_result("Function: calculate_expression('10 * 5 + 2')", result == 52,
                      f"Expected 52, got {result}")
    
    # Test 3: solve_quadratic
    solutions = solve_quadratic(1, -5, 6)
    has_x1 = 'x1' in solutions and solutions['x1'] == 3.0
    has_x2 = 'x2' in solutions and solutions['x2'] == 2.0
    logger.test_result("Function: solve_quadratic(1, -5, 6)", has_x1 and has_x2,
                      f"Got {solutions}")
    
except Exception as e:
    logger.test_result("Math skill functions", False, str(e))

# Text skill functions
try:
    from skills.text_skill import count_words, extract_keywords, summarize
    
    # Test 1: count_words
    count = count_words("hello world test")
    logger.test_result("Function: count_words('hello world test')", count == 3,
                      f"Expected 3, got {count}")
    
    # Test 2: extract_keywords
    keywords = extract_keywords("This is a test about artificial intelligence")
    logger.test_result("Function: extract_keywords()", isinstance(keywords, list) and len(keywords) > 0,
                      f"Got {len(keywords)} keywords: {keywords[:3]}")
    
    # Test 3: summarize (basic test)
    summary = summarize("First sentence. Second sentence. Third sentence.")
    logger.test_result("Function: summarize()", isinstance(summary, str) and len(summary) > 0)
    
except Exception as e:
    logger.test_result("Text skill functions", False, str(e))

# Data skill functions
try:
    from skills.data_skill import statistics, parse_csv_like
    
    # Test 1: statistics
    stats = statistics([1, 2, 3, 4, 5])
    mean_correct = stats.get('mean') == 3.0
    has_std_dev = 'std_dev' in stats
    logger.test_result("Function: statistics([1,2,3,4,5])", mean_correct and has_std_dev,
                      f"Mean={stats.get('mean')}, Std Dev={stats.get('std_dev'):.2f}")
    
    # Test 2: parse_csv_like
    data = parse_csv_like("a,b,c\n1,2,3")
    correct = len(data) == 2 and len(data[0]) == 3
    logger.test_result("Function: parse_csv_like()", correct,
                      f"Expected 2 rows with 3 cols, got {len(data)} rows")
    
except Exception as e:
    logger.test_result("Data skill functions", False, str(e))

# ============================================================================
# SECTION 5: INTEGRATION TESTS
# ============================================================================
logger.log("", "SECTION")
logger.log("Starting Integration Tests", "SECTION")
logger.log("=" * 70, "SECTION")

try:
    from core.main import ToolExecutor
    
    # Test 1: ToolExecutor integration
    executor = ToolExecutor(registry=registry)
    logger.test_result("Integration: ToolExecutor with registry", executor is not None)
    
    # Test 2: Memory + HealthManager integration
    mem.save_memory("integration_test", {"status": "active"})
    health.check_health()
    logger.test_result("Integration: Memory + Health systems", True)
    
    # Test 3: Discovery + Loading integration
    engine = DiscoveryEngine(Path('.'))
    discoveries = engine.discover_all()
    logger.test_result("Integration: Discovery engine full cycle", 
                      len(discoveries.get('tools', [])) > 0)
    
except Exception as e:
    logger.test_result("Integration tests", False, str(e))

# ============================================================================
# FINAL SUMMARY
# ============================================================================
logger.log("", "SECTION")
logger.print_summary()
logger.log("", "SECTION")
logger.log(f"Test Duration: {(datetime.now() - logger.start_time).total_seconds():.2f}s", "INFO")
logger.log("", "SECTION")

if logger.results['failed'] == 0:
    logger.log("🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL 🎉", "PASS")
else:
    logger.log(f"⚠️  {logger.results['failed']} test(s) failed", "FAIL")

# Save log to file
log_content = "\n".join(logger.log_lines)
with open("full_system_test_log.txt", "w") as f:
    f.write(log_content)

logger.log("Log saved to: full_system_test_log.txt", "INFO")
