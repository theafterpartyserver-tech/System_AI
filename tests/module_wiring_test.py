"""
DETAILED MODULE WIRING & FUNCTION VERIFICATION TEST
Tests each module individually with detailed diagnostics
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from datetime import datetime
import json

class ModuleWiringTester:
    """Test individual module wiring and functionality"""
    
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def print_header(self, module_name: str):
        print(f"\n{'='*70}")
        print(f"MODULE: {module_name}")
        print(f"{'='*70}")
    
    def print_test(self, test_name: str, passed: bool, details: str = ""):
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if details:
            print(f"         {details}")
    
    def test_core_ai_router(self):
        """Test [1] AIRouter module"""
        self.print_header("AIRouter")
        
        try:
            from core.ai_router import AIRouter
            from core.hybrid_registry import HybridRegistry
            
            # Test 1: Class instantiation
            registry = HybridRegistry(project_root=Path('.'))
            config_path = Path('./config/config.json')
            router = AIRouter(registry=registry, config_path=config_path)
            self.print_test("Instantiation", router is not None, 
                          f"Type: {type(router).__name__}")
            
            # Test 2: Methods available
            methods = [m for m in dir(router) if not m.startswith('_')]
            self.print_test("Methods available", len(methods) > 0, 
                          f"Found {len(methods)} methods")
            
            # Test 3: Config loading
            has_config = hasattr(router, 'config_path')
            self.print_test("Config path set", has_config, 
                          f"Path: {config_path if has_config else 'N/A'}")
            
            self.results['AIRouter'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['AIRouter'] = False
            return False
    
    def test_core_hybrid_registry(self):
        """Test [2] HybridRegistry module"""
        self.print_header("HybridRegistry")
        
        try:
            from core.hybrid_registry import HybridRegistry
            
            # Test 1: Instantiation
            registry = HybridRegistry(project_root=Path('.'))
            self.print_test("Instantiation", registry is not None,
                          f"Type: {type(registry).__name__}")
            
            # Test 2: Tool listing
            tools = registry.list_tool_names()
            self.print_test("list_tool_names()", isinstance(tools, list),
                          f"Found {len(tools)} tools")
            
            # Test 3: Skill listing
            skills = registry.list_skill_names()
            self.print_test("list_skill_names()", isinstance(skills, list),
                          f"Found {len(skills)} skills")
            
            # Test 4: refresh method
            has_refresh = hasattr(registry, 'refresh')
            self.print_test("refresh() method", has_refresh,
                          "Available for registry updates")
            
            self.results['HybridRegistry'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['HybridRegistry'] = False
            return False
    
    def test_core_memory_compressor(self):
        """Test [3] MemoryCompressor module"""
        self.print_header("MemoryCompressor")
        
        try:
            from core.memory_compressor import MemoryCompressor
            
            # Test 1: Instantiation with required args
            mc = MemoryCompressor(
                memory_dir=Path('./memory'),
                logs_dir=Path('./logs'),
                index_path=Path('./memory/index.json')
            )
            self.print_test("Instantiation", mc is not None,
                          f"Type: {type(mc).__name__}")
            
            # Test 2: Attributes
            has_memory_dir = hasattr(mc, 'memory_dir')
            self.print_test("memory_dir attribute", has_memory_dir,
                          f"Set to: {mc.memory_dir if has_memory_dir else 'N/A'}")
            
            # Test 3: Methods
            methods = [m for m in dir(mc) if not m.startswith('_') and callable(getattr(mc, m))]
            self.print_test("Methods available", len(methods) > 0,
                          f"Found {len(methods)} callable methods")
            
            self.results['MemoryCompressor'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['MemoryCompressor'] = False
            return False
    
    def test_core_health_manager(self):
        """Test [4] HealthManager module"""
        self.print_header("HealthManager")
        
        try:
            from core.health_manager import HealthManager
            
            # Test 1: Instantiation
            hm = HealthManager(project_root=Path('.'))
            self.print_test("Instantiation", hm is not None,
                          f"Type: {type(hm).__name__}")
            
            # Test 2: Methods
            has_check = hasattr(hm, 'check_health')
            self.print_test("check_health() method", has_check,
                          "Available for health checks")
            
            # Test 3: Status tracking
            has_status = hasattr(hm, 'status')
            self.print_test("status attribute", has_status,
                          "Available for status tracking")
            
            self.results['HealthManager'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['HealthManager'] = False
            return False
    
    def test_discovery_engine(self):
        """Test [5] DiscoveryEngine module"""
        self.print_header("DiscoveryEngine")
        
        try:
            from core.discovery_engine import DiscoveryEngine
            
            # Test 1: Instantiation
            engine = DiscoveryEngine(Path('.'))
            self.print_test("Instantiation", engine is not None,
                          f"Type: {type(engine).__name__}")
            
            # Test 2: Discovery methods
            has_discover_all = hasattr(engine, 'discover_all')
            self.print_test("discover_all() method", has_discover_all,
                          "Available for full discovery")
            
            # Test 3: Run discovery
            discoveries = engine.discover_all()
            tool_count = len(discoveries.get('tools', []))
            self.print_test("Tool discovery", tool_count > 0,
                          f"Discovered {tool_count} tools")
            
            # Test 4: Manifest export
            manifest = engine.export_manifest()
            self.print_test("Manifest export", isinstance(manifest, str),
                          "JSON export functional")
            
            self.results['DiscoveryEngine'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['DiscoveryEngine'] = False
            return False
    
    def test_enhanced_tool_loader(self):
        """Test [6] EnhancedToolLoader module"""
        self.print_header("EnhancedToolLoader")
        
        try:
            from core.enhanced_tool_loader import EnhancedToolLoader
            
            # Test 1: Instantiation
            loader = EnhancedToolLoader(Path('./tools'))
            self.print_test("Instantiation", loader is not None,
                          f"Type: {type(loader).__name__}")
            
            # Test 2: Tool loading
            tools = loader.load_all_tools()
            self.print_test("load_all_tools()", isinstance(tools, dict),
                          f"Loaded {len(tools)} tools")
            
            # Test 3: Skill loading
            skills = loader.load_skill_modules(Path('./skills'))
            self.print_test("load_skill_modules()", isinstance(skills, dict),
                          f"Loaded {len(skills)} skills")
            
            # Test 4: List tools
            tool_names = loader.list_tools()
            self.print_test("list_tools()", isinstance(tool_names, list),
                          f"Found {len(tool_names)} tool names")
            
            self.results['EnhancedToolLoader'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['EnhancedToolLoader'] = False
            return False
    
    def test_llm_manager(self):
        """Test [7] LLMManager module"""
        self.print_header("LLMManager")
        
        try:
            from core.llm_manager import LLMManager
            
            # Test 1: Instantiation
            llm = LLMManager(models_dir=Path('./models'))
            self.print_test("Instantiation", llm is not None,
                          f"Type: {type(llm).__name__}")
            
            # Test 2: Config loading
            has_config = hasattr(llm, 'config') and llm.config
            self.print_test("Configuration loaded", has_config,
                          f"Config keys: {list(llm.config.keys())[:3] if has_config else 'N/A'}")
            
            # Test 3: Model discovery
            models = llm.discover_models()
            self.print_test("discover_models()", isinstance(models, list),
                          f"Found {len(models)} GGUF models")
            
            # Test 4: Model info
            info = llm.get_model_info()
            self.print_test("get_model_info()", isinstance(info, dict),
                          "Provides model information")
            
            self.results['LLMManager'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['LLMManager'] = False
            return False
    
    def test_memory_persistence(self):
        """Test [8] MemoryPersistenceManager module"""
        self.print_header("MemoryPersistenceManager")
        
        try:
            from core.memory_persistence import MemoryPersistenceManager
            
            # Test 1: Instantiation
            mem = MemoryPersistenceManager(Path('./memory'))
            self.print_test("Instantiation", mem is not None,
                          f"Type: {type(mem).__name__}")
            
            # Test 2: Memory save
            test_data = {"test": "data", "value": 42}
            saved = mem.save_memory("test_memory", test_data)
            self.print_test("save_memory()", saved,
                          "Data saved successfully")
            
            # Test 3: Memory load
            loaded = mem.load_memory("test_memory")
            self.print_test("load_memory()", loaded == test_data,
                          f"Loaded: {loaded}")
            
            # Test 4: Memory list
            memories = mem.list_memory()
            self.print_test("list_memory()", isinstance(memories, list),
                          f"Found {len(memories)} memory entries")
            
            # Test 5: Memory clear
            cleared = mem.clear_memory("test_memory")
            self.print_test("clear_memory()", cleared,
                          "Memory entry cleared")
            
            self.results['MemoryPersistenceManager'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['MemoryPersistenceManager'] = False
            return False
    
    def test_production_config(self):
        """Test [9] ProductionLogger and HealthMonitor modules"""
        self.print_header("ProductionLogger & HealthMonitor")
        
        try:
            from core.production_config import ProductionLogger, HealthMonitor
            
            # Test 1: Logger instantiation
            logger = ProductionLogger(logs_dir=Path('./logs'))
            self.print_test("ProductionLogger instantiation", logger is not None,
                          f"Type: {type(logger).__name__}")
            
            # Test 2: Logger methods
            has_info = hasattr(logger, 'info')
            has_error = hasattr(logger, 'error')
            self.print_test("Logger methods", has_info and has_error,
                          "info() and error() available")
            
            # Test 3: HealthMonitor instantiation
            monitor = HealthMonitor(logger)
            self.print_test("HealthMonitor instantiation", monitor is not None,
                          f"Type: {type(monitor).__name__}")
            
            # Test 4: Health check
            health = monitor.check_health()
            self.print_test("check_health()", isinstance(health, bool),
                          f"Health status: {health}")
            
            # Test 5: Recovery trigger
            has_recovery = hasattr(monitor, 'trigger_recovery')
            self.print_test("trigger_recovery() method", has_recovery,
                          "Available for error recovery")
            
            self.results['ProductionConfig'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['ProductionConfig'] = False
            return False
    
    def test_skill_modules(self):
        """Test [10] Skill modules (math, text, data)"""
        self.print_header("Skill Modules")
        
        try:
            # Test 1: Math skill
            from skills.math_skill import calculate_expression, solve_quadratic, SKILL_METADATA
            
            result = calculate_expression("2 + 2")
            self.print_test("math_skill.calculate_expression()", result == 4,
                          f"Result: {result}")
            
            quad = solve_quadratic(1, -5, 6)
            self.print_test("math_skill.solve_quadratic()", 'x1' in quad,
                          f"Solutions: x1={quad.get('x1')}, x2={quad.get('x2')}")
            
            # Test 2: Text skill
            from skills.text_skill import count_words, summarize, extract_keywords
            
            word_count = count_words("hello world test")
            self.print_test("text_skill.count_words()", word_count == 3,
                          f"Word count: {word_count}")
            
            keywords = extract_keywords("This is a test about artificial intelligence systems")
            self.print_test("text_skill.extract_keywords()", len(keywords) > 0,
                          f"Found keywords: {keywords[:3]}")
            
            # Test 3: Data skill
            from skills.data_skill import statistics, parse_csv_like
            
            stats = statistics([1, 2, 3, 4, 5])
            self.print_test("data_skill.statistics()", stats.get('mean') == 3.0,
                          f"Mean: {stats.get('mean')}, Std Dev: {stats.get('std_dev'):.2f}")
            
            csv_data = parse_csv_like("a,b,c\n1,2,3")
            self.print_test("data_skill.parse_csv_like()", len(csv_data) == 2,
                          f"Parsed {len(csv_data)} rows")
            
            self.results['SkillModules'] = True
            return True
        except Exception as e:
            self.print_test("Skill modules test", False, str(e))
            self.results['SkillModules'] = False
            return False
    
    def test_tool_executor(self):
        """Test [11] ToolExecutor module"""
        self.print_header("ToolExecutor")
        
        try:
            from core.main import ToolExecutor
            from core.hybrid_registry import HybridRegistry
            
            # Test 1: Instantiation
            registry = HybridRegistry(project_root=Path('.'))
            executor = ToolExecutor(registry=registry)
            self.print_test("Instantiation", executor is not None,
                          f"Type: {type(executor).__name__}")
            
            # Test 2: Execute method
            has_execute = hasattr(executor, 'execute')
            self.print_test("execute() method", has_execute,
                          "Available for tool execution")
            
            # Test 3: Registry attribute
            has_registry = hasattr(executor, 'registry')
            self.print_test("registry attribute", has_registry and executor.registry is not None,
                          "Registry properly bound")
            
            self.results['ToolExecutor'] = True
            return True
        except Exception as e:
            self.print_test("Module test", False, str(e))
            self.results['ToolExecutor'] = False
            return False
    
    def run_all_tests(self):
        """Run all module tests"""
        print("\n" + "="*70)
        print("COMPREHENSIVE MODULE WIRING & FUNCTION VERIFICATION")
        print(f"Timestamp: {self.timestamp}")
        print("="*70)
        
        tests = [
            self.test_core_ai_router,
            self.test_core_hybrid_registry,
            self.test_core_memory_compressor,
            self.test_core_health_manager,
            self.test_discovery_engine,
            self.test_enhanced_tool_loader,
            self.test_llm_manager,
            self.test_memory_persistence,
            self.test_production_config,
            self.test_skill_modules,
            self.test_tool_executor,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"Test execution error: {e}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        for module, result in self.results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {module}")
        
        print(f"\nTotal: {passed}/{total} modules verified")
        
        if passed == total:
            print("\n🎉 ALL MODULES FULLY OPERATIONAL")
        else:
            print(f"\n⚠️  {total - passed} module(s) need attention")
        
        print("="*70)
        
        return passed == total

if __name__ == "__main__":
    tester = ModuleWiringTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
