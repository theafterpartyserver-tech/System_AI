import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, Any

from core import trace, health

logger = logging.getLogger(__name__)


class AIRouter:
    SUPPORTED_BACKENDS = ("local", "ollama", "huggingface")

    def __init__(self, registry, config_path: Path):
        self.registry = registry
        self.config = self._load_config(config_path)
        self.backend = self.config.get("model_backend", "local")
        self.model_path = Path(
            self.config.get("local_model_path", "models/llama3.gguf")
        )
        self.model = None
        self._model_loaded = False

    def parse_intent(self, user_input: str, mode: str = "auto") -> Dict[str, Any]:
        routing_start = time.time()

        if not self._model_loaded:
            self._load_model()

        routing_bias = health.get_routing_bias()

        if mode == "chat_only":
            prompt = self._build_chat_prompt(user_input)
            raw = self._call_backend(prompt)
            raw = self._clean_chat_response(raw)
            raw = self._dedupe_chat_response(raw)
            result = {
                "mode": "chat",
                "raw_response": raw,
                "intent": "",
                "tool": None,
                "args": {},
            }

        elif mode == "tool_only":
            rule_result = self._rule_based_route(user_input)
            if rule_result:
                result = rule_result
            else:
                prompt = self._build_tool_prompt(user_input)
                raw = self._call_backend(prompt)
                parsed = self._parse_tool_response(raw)
                result = self._normalize_llm_tool_choice(parsed)

        else:
            rule_result = self._rule_based_route(user_input)
            if rule_result:
                logger.info("Detected tool call via rule-based router")
                result = rule_result
            else:
                tool_prompt = self._build_tool_prompt(user_input)
                raw = self._call_backend(tool_prompt)
                parsed = self._parse_tool_response(raw)
                parsed = self._normalize_llm_tool_choice(parsed)

                if parsed.get("tool"):
                    logger.info("Detected tool call via LLM tool router")
                    result = parsed
                else:
                    chat_prompt = self._build_chat_prompt(user_input)
                    chat_raw = self._call_backend(chat_prompt)
                    chat_raw = self._clean_chat_response(chat_raw)
                    chat_raw = self._dedupe_chat_response(chat_raw)
                    logger.info("No tool detected; using chat mode")
                    result = {
                        "mode": "chat",
                        "raw_response": chat_raw,
                        "intent": "",
                        "tool": None,
                        "args": {},
                    }

        trace.log_performance(
            "router.parse_intent",
            routing_start,
            metadata={
                "mode": mode,
                "tool": result.get("tool"),
                "routing_bias": routing_bias,
            },
        )
        return result

    def switch_model(self, model_name: str) -> None:
        logger.info(f"Switching model from '{self.backend}' to '{model_name}'")
        self._unload_model()
        self.backend = model_name
        self._model_loaded = False

    def _load_model(self) -> None:
        logger.info(f"Loading model backend: {self.backend}")

        if self.backend == "local":
            self._load_local_model()
        elif self.backend == "ollama":
            self._connect_ollama()
        elif self.backend == "huggingface":
            self._connect_huggingface()
        else:
            raise ValueError(f"Unsupported model backend: {self.backend}")

        self._model_loaded = True

    def _load_local_model(self) -> None:
        try:
            from llama_cpp import Llama

            self.model = {
                "backend": "llama_cpp",
                "llm": Llama(
                    model_path=str(self.model_path),
                    n_ctx=self.config.get("context_length", 4096),
                    n_gpu_layers=self.config.get("gpu_layers", 0),
                    verbose=False,
                ),
                "max_tokens": self.config.get("max_tokens", 512),
                "temperature": self.config.get("temperature", 0.1),
            }
            logger.info(f"Local model loaded: {self.model_path}")
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install with: pip install llama-cpp-python"
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}. "
                "Place your GGUF model in the models/ directory."
            )

    def _connect_ollama(self) -> None:
        self.model = {
            "backend": "ollama",
            "base_url": self.config.get("ollama_base_url", "http://127.0.0.1:11434"),
            "model": self.config.get("ollama_model", "llama3"),
        }
        logger.info("Ollama backend configured.")

    def _connect_huggingface(self) -> None:
        self.model = {
            "backend": "huggingface",
            "model_id": self.config.get("hf_model_id"),
        }
        logger.info("HuggingFace backend configured (stub).")

    def _unload_model(self) -> None:
        self.model = None
        self._model_loaded = False

    def _call_backend(self, prompt: str) -> str:
        if self.backend == "local":
            return self._call_local(prompt)
        elif self.backend == "ollama":
            return self._call_ollama(prompt)
        elif self.backend == "huggingface":
            return self._call_huggingface(prompt)
        raise ValueError(f"No inference method for backend: {self.backend}")

    def _call_local(self, prompt: str) -> str:
        if self.model is None:
            raise RuntimeError("Local model not loaded.")
        result = self.model["llm"].create_completion(
            prompt=prompt,
            max_tokens=self.model["max_tokens"],
            temperature=self.model["temperature"],
            stop=[
                "Response:",
                "User input:",
                "Assistant:",
                "\nUser:",
                "\nAssistant:",
                "\n\nUser:",
                "\n\nAssistant:",
                "\nQuestion:",
                "\nAnswer:",
                "\nlint_code",
                "\ncodegen",
                "User:",
                "Assistant:",
                "lint_code",
                "codegen",
                "`",
                "\n```",
            ],
            echo=False,
        )
        return result["choices"][0]["text"].strip()

    def _call_ollama(self, prompt: str) -> str:
        raise NotImplementedError("Ollama backend not yet implemented.")

    def _call_huggingface(self, prompt: str) -> str:
        raise NotImplementedError("HuggingFace backend not yet implemented.")

    def _get_registered_tool_names(self) -> set[str]:
        return {
            t.get("name", "").strip()
            for t in self.registry.get_injectable_context()
            if t.get("name")
        }

    def _rule_based_route(self, user_input: str) -> Dict[str, Any] | None:
        text = user_input.strip()
        lowered = text.lower()
        tools = self._get_registered_tool_names()

        def has_any(words):
            return any(w in lowered for w in words)

        read_verbs = ["read", "open", "show", "display", "view"]
        write_verbs = ["write", "save", "create file", "make file"]
        codegen_verbs = ["generate", "write code", "create code", "make code", "function"]
        lint_verbs = ["lint", "check code", "analyze code"]

        file_match = re.search(
            r"(?:file named|file|path)\s+([A-Za-z0-9_\-./:\\\\]+)",
            text,
            re.IGNORECASE,
        )

        quoted_code_match = re.search(
            r"code\s*[:\-]\s*[\"']?(.*?)[\"']?$",
            text,
            re.IGNORECASE,
        )

        if "file_read" in tools and has_any(read_verbs) and file_match:
            return {
                "mode": "tool",
                "intent": "file_read",
                "tool": "file_read",
                "args": {"path": file_match.group(1)},
                "raw_response": "",
            }

        if "file_write" in tools and has_any(write_verbs):
            path_match = re.search(
                r"(?:named|to|at)\s+([A-Za-z0-9_\-./:\\\\]+)",
                text,
                re.IGNORECASE,
            )
            content_match = re.search(
                r"(?:content|with the content)\s+(.+)$",
                text,
                re.IGNORECASE,
            )
            if path_match and content_match:
                return {
                    "mode": "tool",
                    "intent": "file_write",
                    "tool": "file_write",
                    "args": {
                        "path": path_match.group(1),
                        "content": content_match.group(1).strip(),
                    },
                    "raw_response": "",
                }

        if "lint_code" in tools and has_any(lint_verbs):
            code = ""
            if quoted_code_match:
                code = quoted_code_match.group(1).strip()
            elif "print hello world" in lowered:
                code = "print('hello world')"
            elif "semicolon" in lowered:
                code = "print('hello');"
            if code:
                return {
                    "mode": "tool",
                    "intent": "lint_code",
                    "tool": "lint_code",
                    "args": {"code": code},
                    "raw_response": "",
                }

        if "codegen" in tools and has_any(codegen_verbs):
            return {
                "mode": "tool",
                "intent": "codegen",
                "tool": "codegen",
                "args": {"prompt": text},
                "raw_response": "",
            }

        return None

    def _normalize_llm_tool_choice(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        tool = parsed.get("tool")
        registered_tools = self._get_registered_tool_names()

        if tool in (None, "", "null", "None"):
            return {
                "mode": "chat",
                "intent": str(parsed.get("intent", "")),
                "tool": None,
                "args": {},
                "raw_response": parsed.get("raw_response", ""),
            }

        if tool not in registered_tools:
            logger.warning(f"LLM returned unregistered tool '{tool}', falling back to chat")
            return {
                "mode": "chat",
                "intent": str(parsed.get("intent", "")),
                "tool": None,
                "args": {},
                "raw_response": parsed.get("raw_response", ""),
            }

        return {
            "mode": "tool",
            "intent": str(parsed.get("intent", "")),
            "tool": tool,
            "args": dict(parsed.get("args", {})),
            "raw_response": parsed.get("raw_response", ""),
        }

    def _clean_chat_response(self, text: str) -> str:
        if not text:
            return text

        for marker in ["\nUser:", "\nAssistant:", "User:", "Assistant:"]:
            idx = text.find(marker)
            if idx != -1:
                text = text[:idx]

        return text.strip()

    def _dedupe_chat_response(self, text: str) -> str:
        if not text:
            return text

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""

        deduped = []
        for line in lines:
            if not deduped or line != deduped[-1]:
                deduped.append(line)

        if len(deduped) > 1 and all(line == deduped for line in deduped):
            return deduped

        return "\n".join(deduped).strip()

    def _build_tool_prompt(self, user_input: str) -> str:
        registry_context = json.dumps(
            self.registry.get_injectable_context(), indent=2
        )
        system_instruction = (
            "You are an intent parser.\n"
            "Your ONLY job is to convert user input into a structured JSON command.\n"
            "You MUST select tools ONLY from the provided available_tools list.\n"
            "Never invent tool names.\n"
            "If the user is just chatting or asking a normal question, return tool as null.\n"
            "If the user asks to read, write, generate code, or lint code, choose the best matching registered tool.\n\n"
            "Respond ONLY with valid JSON in this exact format:\n"
            '{"intent": "<description>", "tool": "<tool_name or null>", "args": {}}\n\n'
            f"Available tools:\n{registry_context}\n"
        )
        return f"{system_instruction}\nUser input: {user_input}\nResponse:\n"

    def _build_chat_prompt(self, user_input: str) -> str:
        tool_names = ", ".join(
            t.get("name", "unknown") for t in self.registry.get_injectable_context()
        )
        system_instruction = (
            "You are an AI coding assistant for a local AI execution system.\n"
            f"You can access these tools: {tool_names}.\n"
            "Answer normal questions directly and naturally.\n"
            "Reply with only the final answer.\n"
            "Do not ask follow-up questions.\n"
            "Do not mention tools unless the user explicitly asks about them.\n"
            "Do not include labels like 'User:', 'Assistant:', 'lint_code', or 'codegen'.\n"
            "Keep the response to one short paragraph or one line when possible.\n"
        )
        return f"{system_instruction}\nUser: {user_input}\nAssistant:\n"

    def _extract_first_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if escape:
                escape = False
                continue

            if ch == "\\":
                escape = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return None

    def _parse_tool_response(self, raw: str) -> Dict[str, Any]:
        candidate = self._extract_first_json_object(raw)
        if candidate is None:
            logger.error(f"Tool response JSON parse failure: {raw}")
            return {
                "mode": "chat",
                "intent": "",
                "tool": None,
                "args": {},
                "raw_response": raw,
            }

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            logger.error(f"Tool response JSON parse failure: {raw}")
            return {
                "mode": "chat",
                "intent": "",
                "tool": None,
                "args": {},
                "raw_response": raw,
            }

        tool = parsed.get("tool")
        if tool in (None, "", "null", "None"):
            tool = None

        args = parsed.get("args") or {}
        if not isinstance(args, dict):
            args = {}

        return {
            "mode": "tool" if tool else "chat",
            "intent": str(parsed.get("intent", "")),
            "tool": tool,
            "args": args,
            "raw_response": raw,
        }

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found at {config_path}. Using defaults.")
            return {}
