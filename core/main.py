import sys
import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.hybrid_registry import HybridRegistry
from core.integration.main_glue import setup_context
from core.integration.wiring import IntegratedRouter
from core.memory import MemoryPersistenceManager
from core.llm_manager import LLMManager


CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
MEMORY_DIR = PROJECT_ROOT / "memory"


class SystemAI:

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.config_path = CONFIG_PATH
        self.memory_dir = MEMORY_DIR

        print("\n" + "=" * 70)
        print("SYSTEM AI - LLM Chat + Tool Router (Integrated Edition)")
        print("=" * 70)
        print("\n[INIT] Initializing registry and discovering components...")

        self.registry = HybridRegistry(project_root=self.project_root)

        print("[INIT] Setting up application context...")
        self.context = setup_context(
            registry=self.registry,
            config_path=self.config_path,
            model_path=self.project_root / "models",
            state_dir=self.project_root / "runtime",
        )

        print("[INIT] Initializing integrated router...")
        self.router = IntegratedRouter(self.context)

        print("[INIT] Loading LLM model...")
        self.llm_manager = LLMManager(
            models_dir=self.project_root / "models",
            config_path=self.config_path,
        )

        self.config = json.loads(self.config_path.read_text())
        default_model = self.config.get("local_model_path", "").split("/")[-1].replace(".gguf", "")
        if default_model:
            self.llm_manager.load_model(default_model)

        print("[INIT] Initializing memory persistence...")
        self.mem_persistence = MemoryPersistenceManager(self.memory_dir)

        print("\n[INIT] System ready. Type 'help' for commands.\n")
        print("-" * 70)
        print(self.generate_dynamic_help())

    def generate_dynamic_help(self) -> str:
        tools = self.registry.list_tool_names()
        skills = self.registry.list_skill_names()
        help_text = """
Available Commands:
  help           - Show this help message
  status         - Show system status
  tools          - List available tools
  skills         - List available skills
  memory         - Show memory stats
  discover       - Discover components
  scan <path>    - Scan a directory
  exit/quit      - Exit the program

Available Tools:
"""
        for tool in sorted(tools):
            tool_spec = self.registry.get_tool(tool)
            if tool_spec:
                help_text += f"  * {tool} - {tool_spec.description}\n"

        if skills:
            help_text += "\nAvailable Skills:\n"
            for skill in sorted(skills):
                help_text += f"  * {skill}\n"

        return help_text

    def handle_help(self):
        print(self.generate_dynamic_help())

    def handle_status(self):
        print("\nSystem Status:")
        print(f"  Registry initialized")
        print(f"  Tools discovered: {len(self.registry.list_tool_names())}")
        print(f"  Skills discovered: {len(self.registry.list_skill_names())}")
        print(f"  Health monitoring: {'active' if self.context.health_manager else 'inactive'}")
        print(f"  Memory persistence: ready")
        print(f"  LLM model: {'loaded' if self.llm_manager.current_model else 'not loaded'}")
        print(f"  Router integrated: ready")
        print(f"  FS access tier: {self.config.get('fs_access', 'project')}")

    def handle_tools(self):
        tools = self.registry.list_tool_names()
        print("\nAvailable Tools:")
        if tools:
            for tool in sorted(tools):
                spec = self.registry.get_tool(tool)
                if spec:
                    print(f"  * {tool} [{spec.risk}] - {spec.description}")
        else:
            print("  (No tools registered)")

    def handle_skills(self):
        skills = self.registry.list_skill_names()
        print("\nAvailable Skills:")
        if skills:
            for skill in sorted(skills):
                print(f"  * {skill}")
        else:
            print("  (No skills discovered)")

    def handle_memory(self):
        stats = self.mem_persistence.get_stats()
        print("\nMemory Statistics:")
        print(f"  Entries stored: {stats['entries']}")
        print(f"  Total size: {stats['total_size_bytes']} bytes")
        if stats['created']:
            print(f"  Created: {stats['created']}")
        memory_list = self.mem_persistence.list_memory()
        if memory_list:
            print("\n  Stored memories:")
            for key in memory_list[:10]:
                print(f"    - {key}")
            if len(memory_list) > 10:
                print(f"    ... and {len(memory_list) - 10} more")

    def handle_discover(self):
        print("\nSystem Component Discovery:")
        print(f"  Tools: {len(self.registry.list_tool_names())} discovered")
        print(f"  Skills: {len(self.registry.list_skill_names())} discovered")
        print(f"  Models: Check models/ directory")

    def handle_scan(self, user_input: str):
        target = user_input.strip()[4:].strip().strip('"\'') or '.'
        p = Path(target)
        if not p.exists():
            print(f"  Path not found: {target}")
            return
        if not p.is_dir():
            print(f"  Not a directory: {target}")
            return
        print(f"\nContents of {p.resolve()}:")
        dirs = []
        files = []
        for item in sorted(p.iterdir()):
            if item.is_dir():
                dirs.append(item.name)
            else:
                files.append(item.name)
        for d in dirs:
            print(f"  [DIR]  {d}")
        for f in files:
            print(f"  [FILE] {f}")
        print(f"\n  {len(dirs)} dirs, {len(files)} files")

    def _extract_path(self, user_input: str) -> str:
        quoted = re.findall(r'["\']([^"\']+)["\']', user_input)
        if quoted:
            return quoted[0]
        tokens = user_input.split()
        for token in tokens:
            if ("." in token or "/" in token or "\\" in token) and not token.startswith("-"):
                return token
        return user_input

    def _check_fs_access(self, user_input: str) -> bool:
        fs_access = self.config.get("fs_access", "project")
        quoted_paths = re.findall(r'["\']([^"\']+)["\']', user_input)
        for qp in quoted_paths:
            qpp = Path(qp)
            if qpp.is_absolute() and str(self.project_root) not in str(qpp):
                if fs_access == "project":
                    print(f"\n[BLOCKED] Path outside project root: {qp}")
                    print("Set fs_access to 'local' or 'unrestricted' in config/config.json")
                    return False
                elif fs_access == "local":
                    print(f"\n[WARNING] Accessing external path: {qp}")
        return True

    def handle_user_input(self, user_input: str):
        if not self._check_fs_access(user_input):
            return

        try:
            result = self.router.parse_intent(user_input, mode="auto")

            if result.get("mode") == "tool":
                tool_name = result.get("tool")
                print(f"\n[TOOL] Executing: {tool_name}")
                try:
                    path_arg = self._extract_path(user_input)

                    if tool_name == "file_read":
                        tool_result = self.context.registry.execute_tool(tool_name, path=path_arg)
                        response = (
                            tool_result.get("content")
                            or tool_result.get("error")
                            or str(tool_result)
                        )

                    elif tool_name == "list_dir":
                        tool_result = self.context.registry.execute_tool(tool_name, path=path_arg)
                        items = tool_result.get("items", [])
                        if items:
                            response = "\n".join(
                                f"  [{i['type']}] {i['name']}" for i in items
                            )
                        else:
                            response = tool_result.get("error") or "Empty directory"

                    elif tool_name == "file_write":
                        response = "file_write requires path and content - use: write <path> <content>"

                    elif tool_name in ("lint_code", "codegen"):
                        tool_result = self.context.registry.execute_tool(
                            tool_name, prompt=user_input
                        )
                        response = (
                            tool_result.get("output")
                            or tool_result.get("result")
                            or tool_result.get("error")
                            or str(tool_result)
                        )

                    elif tool_name == "shell_exec":
                        tool_result = self.context.registry.execute_tool(
                            tool_name, command=user_input
                        )
                        response = (
                            tool_result.get("stdout")
                            or tool_result.get("output")
                            or tool_result.get("error")
                            or str(tool_result)
                        )

                    else:
                        tool_result = self.context.registry.execute_tool(
                            tool_name, prompt=user_input
                        )
                        response = str(tool_result)

                except Exception as te:
                    response = f"Tool error: {te}"
                print(f"Response:\n{response}")

            else:
                response = self.llm_manager.generate(user_input)
                print(f"\nResponse: {response}")

            entry_num = self.mem_persistence.get_stats()["entries"] + 1
            self.mem_persistence.save_memory(
                key=f"turn_{entry_num:04d}",
                data={"input": user_input, "response": response},
                metadata={"mode": result.get("mode", "chat")},
            )

        except Exception as e:
            print(f"Error processing input: {e}")

    def run(self) -> None:
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                command = user_input.lower().strip(".,!?").split()[0]

                if command in ["exit", "quit"]:
                    print("\nGoodbye!")
                    break
                elif command == "help":
                    self.handle_help()
                elif command == "status":
                    self.handle_status()
                elif command == "tools":
                    self.handle_tools()
                elif command == "skills":
                    self.handle_skills()
                elif command == "memory":
                    self.handle_memory()
                elif command == "discover":
                    self.handle_discover()
                elif command == "scan":
                    self.handle_scan(user_input)
                else:
                    self.handle_user_input(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main() -> None:
    try:
        system = SystemAI()
        system.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
