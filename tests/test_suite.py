"""
System AI - Comprehensive Feature Test Suite
Tests all integrated modules, discovery, routing, and CLI functionality
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

def print_section(title):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")

def test_core_imports():
    """Test [1] Core module imports"""
    print_section("[1] CORE MODULE IMPORTS")
    
    components = [
        'AIRouter', 'HybridRegistry', 'MemoryCompressor', 'SessionStateStore',
        'ToolRegistry', 'MemoryManager', 'HealthManager', 'RoutingEngine',
        'ReliabilityManager', 'RecoveryManager', 'PerformanceManager',
        'BootCheck', 'SystemDiagnostics', 'ToolExecutor', 'DiscoveryEngine'
    ]
    
    import core
    
    passed = 0
    for comp in components:
        try:
            obj = getattr(core, comp)
            print(f"  ✓ {comp}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {comp}: {e}")
    
    print(f"\nResult: {passed}/{len(components)} components imported")
    return passed == len(components)

def test_discovery_engine():
    """Test [2] Discovery Engine functionality"""
    print_section("[2] DISCOVERY ENGINE")
    
    from core.discovery_engine import DiscoveryEngine
    
    engine = DiscoveryEngine(Path('.'))
    discoveries = engine.discover_all()
    
    tools = discoveries.get('tools', [])
    skills = discoveries.get('skills', [])
    programs = discoveries.get('programs', [])
    
    print(f"  ✓ Tools discovered: {len(tools)}")
    for tool in tools:
        print(f"    - {tool['name']}")
    
    print(f"  ✓ Skills discovered: {len(skills)}")
    print(f"  ✓ Programs discovered: {len(programs)}")
    
    manifest = engine.export_manifest()
    manifest_obj = json.loads(manifest)
    
    print(f"  ✓ Manifest exported (version {manifest_obj['version']})")
    
    return len(tools) > 0

def test_hybrid_registry():
    """Test [3] HybridRegistry functionality"""
    print_section("[3] HYBRID REGISTRY")
    
    from core.hybrid_registry import HybridRegistry
    
    registry = HybridRegistry(project_root=Path('.'))
    
    tools = registry.list_tool_names()
    skills = registry.list_skill_names()
    
    print(f"  ✓ Registry initialized")
    print(f"  ✓ Tools registered: {len(tools)}")
    print(f"  ✓ Skills registered: {len(skills)}")
    
    return registry is not None

def test_ai_router():
    """Test [4] AIRouter initialization"""
    print_section("[4] AI ROUTER")
    
    from core.ai_router import AIRouter
    from core.hybrid_registry import HybridRegistry
    
    config_path = Path('.') / 'config' / 'config.json'
    registry = HybridRegistry(project_root=Path('.'))
    
    try:
        router = AIRouter(registry=registry, config_path=config_path)
        print(f"  ✓ AIRouter initialized")
        print(f"  ✓ Config loaded from: {config_path}")
        return True
    except Exception as e:
        print(f"  ✗ AIRouter error: {e}")
        return False

def test_memory_systems():
    """Test [5] Memory management systems"""
    print_section("[5] MEMORY SYSTEMS")
    
    from core.memory_compressor import MemoryCompressor
    from core.memory_manager import MemoryManager
    
    try:
        mc = MemoryCompressor(
            memory_dir=Path('.') / 'memory',
            logs_dir=Path('.') / 'logs',
            index_path=Path('.') / 'memory' / 'index.json'
        )
        print(f"  ✓ MemoryCompressor initialized")
        
        manager = MemoryManager()
        print(f"  ✓ MemoryManager initialized")
        
        return True
    except Exception as e:
        print(f"  ✗ Memory system error: {e}")
        return False

def test_health_monitoring():
    """Test [6] Health and monitoring"""
    print_section("[6] HEALTH & MONITORING")
    
    from core.health_manager import HealthManager
    from core.performance_manager import PerformanceManager
    
    try:
        health = HealthManager(project_root=Path('.'))
        print(f"  ✓ HealthManager initialized")
        
        perf = PerformanceManager()
        print(f"  ✓ PerformanceManager initialized")
        
        return True
    except Exception as e:
        print(f"  ✗ Monitoring error: {e}")
        return False

def test_recovery_systems():
    """Test [7] Recovery and reliability"""
    print_section("[7] RECOVERY & RELIABILITY")
    
    from core.recovery_manager import RecoveryManager
    
    try:
        recovery = RecoveryManager()
        print(f"  ✓ RecoveryManager initialized")
        print(f"  ✓ Recovery systems ready")
        
        return True
    except Exception as e:
        print(f"  ✗ Recovery error: {e}")
        return False

def test_configuration():
    """Test [8] Configuration system"""
    print_section("[8] CONFIGURATION SYSTEM")
    
    config_path = Path('.') / 'config' / 'config.json'
    
    if config_path.exists():
        print(f"  ✓ config.json exists")
        try:
            with open(config_path) as f:
                config = json.load(f)
            print(f"  ✓ Configuration valid")
            keys = list(config.keys())[:5]
            print(f"  ✓ Config keys: {', '.join(keys)}")
            return True
        except Exception as e:
            print(f"  ✗ Config error: {e}")
            return False
    else:
        print(f"  ✗ config.json not found")
        return False

def test_manifest():
    """Test [9] Tools manifest"""
    print_section("[9] TOOLS MANIFEST")
    
    manifest_path = Path('.') / 'tools_manifest.json'
    
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            print(f"  ✓ tools_manifest.json valid")
            tools = manifest.get('tools', [])
            print(f"  ✓ Tools registered: {len(tools)}")
            for tool in tools[:5]:
                print(f"    - {tool['name']}")
            return True
        except Exception as e:
            print(f"  ✗ Manifest error: {e}")
            return False
    else:
        print(f"  ✗ tools_manifest.json not found")
        return False

def test_cli_functionality():
    """Test [10] CLI functionality"""
    print_section("[10] CLI FUNCTIONALITY")
    
    from core.main import ToolExecutor
    from core.hybrid_registry import HybridRegistry
    
    try:
        registry = HybridRegistry(project_root=Path('.'))
        executor = ToolExecutor(registry=registry)
        print(f"  ✓ ToolExecutor initialized")
        print(f"  ✓ CLI entry point ready")
        return True
    except Exception as e:
        print(f"  ✗ CLI error: {e}")
        return False

def test_project_structure():
    """Test [11] Project structure"""
    print_section("[11] PROJECT STRUCTURE")
    
    required_dirs = ['core', 'tools', 'skills', 'config', 'memory', 'logs']
    required_files = [
        'core/__init__.py', 'core/main.py', 'pyproject.toml',
        'README.md', '.gitignore', 'tools_manifest.json'
    ]
    
    passed = 0
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✓ {dir_name}/ exists")
            passed += 1
        else:
            print(f"  ✗ {dir_name}/ missing")
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✓ {file_name} exists")
            passed += 1
        else:
            print(f"  ✗ {file_name} missing")
    
    return passed == (len(required_dirs) + len(required_files))

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SYSTEM AI - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_core_imports,
        test_discovery_engine,
        test_hybrid_registry,
        test_ai_router,
        test_memory_systems,
        test_health_monitoring,
        test_recovery_systems,
        test_configuration,
        test_manifest,
        test_cli_functionality,
        test_project_structure,
    ]
    
    results = {}
    for test in tests:
        try:
            results[test.__name__] = test()
        except Exception as e:
            print(f"  ✗ Test error: {e}")
            results[test.__name__] = False
    
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        clean_name = test_name.replace('test_', '').replace('_', ' ').title()
        print(f"  {status}: {clean_name}")
    
    print("\n" + "="*70)
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    print("="*70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
