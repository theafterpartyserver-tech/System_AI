# system_ai

Local CLI AI shell with tool-driven routing, permissions, health checks, and memory. Built in 4 months as a Claude Code–style agent for local LLM inference.

## Quick Start

\\\ash
cd system_ai
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/macOS

pip install -e .
python core/main.py
\\\

Type \help\ for CLI menu.

## Features

- **Rules + LLM routing**: Switches between chat and tools (\ile_read\, \ile_write\, \lint_code\, \codegen\).
- **Permissions**: File writes and shell commands require approval; enforced via \Gateway\.
- **Health & diagnostics**: Boot checks, system diagnostics, health manager, regression suite, release gate.
- **Memory & recovery**: Session state, snapshots, and recovery prompting for crash resilience.
- **Local inference**: Llama.cpp + GGUF models (Llama-3.2-3B-Instruct Q4_K_M recommended).
- **Observability**: Structured logs, latency tracking, performance metrics, regression tests.

## Architecture

- **core/**: Main modules (routing, tools, permissions, health, memory, tests, recovery).
- **config/**: Configuration files (model, permissions, sandbox policies).
- **models/**: Local GGUF model files (18 quantizations of Llama-3.2-3B-Instruct available).
- **skills/**: Markdown workflow definitions.
- **logs/, memory/, runtime/**: Runtime state and artifacts.

## System Requirements

- **OS**: Windows 11, Linux, or macOS.
- **Python**: 3.11+
- **RAM**: ~7.5 GB (8+ recommended for smooth operation).
- **GPU**: NVIDIA (CUDA 12.1+) recommended; CPU-only supported.

### Tested Hardware

- ASUS TUF Gaming A17 FA706IH: Ryzen 5 4600H, GTX 1650 (4GB), 7.6GB RAM.

## Configuration

Edit these files in \config/\:

- **config.json**: Model backend, context length, temperature, routing bias.
- **permissions.json**: Tool risk tiers (safe, elevated, dangerous).
- **sandbox.json**: Restricted and allowed paths for file tools.

## Tools

- \ile_read\: Read file contents (safe).
- \ile_write\: Write to files (elevated).
- \lint_code\: Lint code snippets (safe).
- \codegen\: Generate code via LLM (safe).
- \system_diagnostics\: Health and system info (safe).

## Development

Install dev dependencies:

\\\ash
pip install -e ".[dev]"
pytest  # Run test suite
black core/  # Format code
ruff check core/  # Lint
\\\

## Roadmap

- [ ] Permission modes (default/plan/acceptEdits/auto).
- [ ] Semantic search for repository understanding.
- [ ] HTTP API for editor integrations.
- [ ] More tools (shell execution, advanced refactoring).
- [ ] Multi-session workflows and agent coordination.

## License

MIT

## Author

Built by Menace2Tech in 4 months of focused development.
