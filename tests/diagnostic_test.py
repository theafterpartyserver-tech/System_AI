import sys
sys.path.insert(0, '.')
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("🧪 SYSTEM AI - COMPREHENSIVE DIAGNOSTIC TEST")
print("=" * 70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# Test 1: IMPORTS
print("[1] TESTING IMPORTS")
print("-" * 70)
imports = [
    ("AIRouter", "from core.ai_router import AIRouter"),
    ("HybridRegistry", "from core.hybrid_registry import HybridRegistry"),
    ("MemoryCompressor", "from core.memory_compressor import MemoryCompressor"),
    ("HealthManager", "from core.health_manager_enhanced import HealthManager"),
    ("DiscoveryEngine", "from core.discovery_engine import DiscoveryEngine"),
    ("EnhancedToolLoader", "from core.enhanced_tool_loader import EnhancedToolLoader"),
    ("LLMManager", "from core.llm_manager import LLMManager"),
    ("MemoryPersistenceManager", "from core.memory_persistence import MemoryPersistenceManager"),
    ("ProductionLogger", "from core.production_config import ProductionLogger"),
    ("ToolExecutor", "from core.main import ToolExecutor"),
]

import_pass = 0
for name, import_code in imports:
    try:
        exec(import_code)
        print(f"✅ {name}")
        import_pass += 1
    except Exception as e:
        print(f"❌ {name}: {str(e)[:40]}")

print(f"\nImports: {import_pass}/{len(imports)} passed\n")

# Test 2: WIRING
print("[2] TESTING WIRING (Module Connections)")
print("-" * 70)

wiring_pass = 0
try:
    from core.hybrid_registry import HybridRegistry
    registry = HybridRegistry(project_root=Path('.'))
    print("✅ HybridRegistry wired to project_root")
    wiring_pass += 1
except Exception as e:
    print(f"❌ HybridRegistry: {e}")

try:
    from core.ai_router import AIRouter
    router = AIRouter(registry=registry, config_path=Path('./config/config.json'))
    print("✅ AIRouter wired to HybridRegistry")
    wiring_pass += 1
except Exception as e:
    print(f"❌ AIRouter: {e}")

try:
    from core.memory_persistence import MemoryPersistenceManager
    mem = MemoryPersistenceManager(Path('./memory'))
    print("✅ MemoryPersistenceManager wired to memory_dir")
    wiring_pass += 1
except Exception as e:
    print(f"❌ MemoryPersistenceManager: {e}")

try:
    from core.health_manager_enhanced import HealthManager
    health = HealthManager(project_root=Path('.'))
    print("✅ HealthManager wired to project_root")
    wiring_pass += 1
except Exception as e:
    print(f"❌ HealthManager: {e}")

print(f"\nWiring: {wiring_pass}/4 passed\n")

# Test 3: LOGIC
print("[3] TESTING LOGIC (Execution Flows)")
print("-" * 70)

logic_pass = 0
try:
    from core.discovery_engine import DiscoveryEngine
    engine = DiscoveryEngine(Path('.'))
    discoveries = engine.discover_all()
    tools_count = len(discoveries.get('tools', []))
    print(f"✅ Discovery engine logic: Found {tools_count} tools")
    logic_pass += 1
except Exception as e:
    print(f"❌ Discovery: {e}")

try:
    stats = mem.get_stats()
    print("✅ Memory stats logic: Retrieved stats")
    logic_pass += 1
except Exception as e:
    print(f"❌ Memory stats: {e}")

try:
    health_check = health.check_health()
    print(f"✅ Health check logic: Status={health_check}")
    logic_pass += 1
except Exception as e:
    print(f"❌ Health check: {e}")

try:
    from core.enhanced_tool_loader import EnhancedToolLoader
    loader = EnhancedToolLoader(Path('./tools'))
    skills = loader.load_skill_modules(Path('./skills'))
    print(f"✅ Skill loading logic: Loaded {len(skills)} skills")
    logic_pass += 1
except Exception as e:
    print(f"❌ Skill loading: {e}")

print(f"\nLogic: {logic_pass}/4 passed\n")

# Test 4: FUNCTIONS
print("[4] TESTING FUNCTIONS (Individual Operations)")
print("-" * 70)

func_pass = 0

try:
    from skills.math_skill import calculate_expression, solve_quadratic
    result1 = calculate_expression("2 + 2")
    result2 = solve_quadratic(1, -5, 6)
    print(f"✅ math_skill.calculate_expression('2+2') = {result1}")
    print(f"✅ math_skill.solve_quadratic(1,-5,6) = {result2}")
    func_pass += 2
except Exception as e:
    print(f"❌ Math skills: {e}")

try:
    from skills.text_skill import count_words, extract_keywords
    result1 = count_words("hello world test")
    result2 = extract_keywords("This is a test about AI systems")
    print(f"✅ text_skill.count_words() = {result1}")
    print(f"✅ text_skill.extract_keywords() = {len(result2)} keywords")
    func_pass += 2
except Exception as e:
    print(f"❌ Text skills: {e}")

try:
    from skills.data_skill import statistics, parse_csv_like
    result1 = statistics([1, 2, 3, 4, 5])
    result2 = parse_csv_like("a,b\n1,2")
    print(f"✅ data_skill.statistics([1..5]) = mean={result1.get('mean')}")
    print(f"✅ data_skill.parse_csv_like() = {len(result2)} rows")
    func_pass += 2
except Exception as e:
    print(f"❌ Data skills: {e}")

print(f"\nFunctions: {func_pass}/6 passed\n")

# SUMMARY
print("=" * 70)
print("📊 FINAL SUMMARY")
print("=" * 70)
total_pass = import_pass + wiring_pass + logic_pass + func_pass
total_tests = len(imports) + 4 + 4 + 6
success_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {total_pass}")
print(f"❌ Failed: {total_tests - total_pass}")
print(f"📊 Success Rate: {success_rate:.1f}%")
print()

if total_pass == total_tests:
    print("🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL 🎉")
else:
    print(f"⚠️  {total_tests - total_pass} test(s) need attention")

print("=" * 70)
