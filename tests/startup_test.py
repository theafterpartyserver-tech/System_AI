import os, sys
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)


import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Initialize logging
log_file = Path("startup_test.log")
log_messages = []

def log(msg):
    print(msg)
    log_messages.append(msg)

def log_error(msg, exc=None):
    log(f"[ERROR] {msg}")
    if exc:
        log(f"  Details: {str(exc)}")
    log_messages.append(f"ERROR: {msg}")

log("\\n" + "=" * 70)
log("SYSTEM STARTUP VERIFICATION TEST")
log("=" * 70)

# Test 1: Direct imports with graceful fallback
log("\\n[TEST 1] Attempting core imports...")
imports_ok = True
try:
    from core.hybrid_registry import HybridRegistry
    log("  [OK] HybridRegistry")
except Exception as e:
    log_error("HybridRegistry import", e)
    imports_ok = False

try:
    from core.app_context import AppContext
    log("  [OK] AppContext")
except Exception as e:
    log_error("AppContext import", e)
    imports_ok = False

try:
    from core.integration.wiring import IntegratedRouter
    log("  [OK] IntegratedRouter")
except Exception as e:
    log_error("IntegratedRouter import", e)
    imports_ok = False

# Test 2: Check configuration files exist
log("\\n[TEST 2] Checking configuration files...")
config_files = {
    "config.json": PROJECT_ROOT / "config" / "config.json",
    "permissions.json": PROJECT_ROOT / "config" / "permissions.json",
    "sandbox.json": PROJECT_ROOT / "config" / "sandbox.json",
    "tools_manifest.json": PROJECT_ROOT / "tools" / "tools_manifest.json",
}

configs_ok = True
for name, path in config_files.items():
    if path.exists():
        try:
            json.loads(path.read_text())
            log(f"  [OK] {name}")
        except Exception as e:
            log_error(f"{name} (invalid JSON)", e)
            configs_ok = False
    else:
        log_error(f"{name} (not found)")
        configs_ok = False

# Test 3: Check directory structure
log("\\n[TEST 3] Checking directory structure...")
dirs = {
    "core": PROJECT_ROOT / "core",
    "config": PROJECT_ROOT / "config",
    "models": PROJECT_ROOT / "models",
    "skills": PROJECT_ROOT / "skills",
    "tools": PROJECT_ROOT / "tools",
    "memory": PROJECT_ROOT / "memory",
    "logs": PROJECT_ROOT / "logs",
    "runtime": PROJECT_ROOT / "runtime",
}

dirs_ok = True
for name, path in dirs.items():
    if path.exists() and path.is_dir():
        log(f"  [OK] {name}/")
    else:
        log_error(f"{name}/ (missing)")
        dirs_ok = False

# Test 4: Check models exist
log("\\n[TEST 4] Checking GGUF models...")
models_dir = PROJECT_ROOT / "models"
gguf_files = list(models_dir.glob("*.gguf")) if models_dir.exists() else []
log(f"  Found {len(gguf_files)} GGUF models")
if gguf_files:
    for model in sorted(gguf_files)[:5]:
        log(f"    - {model.name}")
    if len(gguf_files) > 5:
        log(f"    ... and {len(gguf_files) - 5} more")

# Test 5: Try registry initialization if imports worked
if imports_ok:
    log("\\n[TEST 5] Initializing HybridRegistry...")
    try:
        from core.hybrid_registry import HybridRegistry
        registry = HybridRegistry(project_root=PROJECT_ROOT)
        tools = registry.list_tool_names()
        skills = registry.list_skill_names()
        log(f"  [OK] Registry initialized")
        log(f"    Tools discovered: {len(tools)}")
        log(f"    Skills discovered: {len(skills)}")
    except Exception as e:
        log_error("Registry initialization", e)

# Final report
log("\\n" + "=" * 70)
if imports_ok and configs_ok and dirs_ok:
    log("RESULT: STARTUP VERIFICATION PASSED")
    log("System structure is intact and ready for full testing")
else:
    log("RESULT: STARTUP VERIFICATION COMPLETED WITH WARNINGS")
    log("See log for details")

log("=" * 70)

# Save log with UTF-8 encoding
try:
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\\n".join(log_messages))
    print(f"\\nLog saved to: {log_file}")
except Exception as e:
    print(f"Warning: Could not save log file: {e}")




