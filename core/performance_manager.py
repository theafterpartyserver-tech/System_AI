from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import time


@dataclass
class PerformanceSample:
    name: str
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class PerformanceConfig:
    model_warm_start: bool = True
    lazy_load_tools: bool = True
    lazy_load_skills: bool = True
    cache_config: bool = True
    cache_registry: bool = True
    cache_prompts: bool = True
    max_context_length: int = 4096
    max_chat_tokens: int = 256
    max_tool_tokens: int = 256
    inference_timeout_seconds: float = 20.0


class PerformanceManager:
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self._prompt_cache: Dict[str, str] = {}
        self._config_cache: Dict[str, Any] = {}
        self._registry_cache: Dict[str, Any] = {}
        self._samples: list[PerformanceSample] = []
        self._warm_state: Dict[str, Any] = {}

    def warm_start_model(self, model_name: str) -> Dict[str, Any]:
        self._warm_state.update({"model_name": model_name, "warmed_at": time.time()})
        return {"status": "ok", "model_name": model_name}

    def cache_prompt(self, key: str, prompt: str) -> None: self._prompt_cache[key] = prompt
    def get_cached_prompt(self, key: str) -> Optional[str]: return self._prompt_cache.get(key)
    def cache_config(self, key: str, value: Any) -> None: self._config_cache[key] = value
    def get_cached_config(self, key: str) -> Any: return self._config_cache.get(key)
    def cache_registry(self, key: str, value: Any) -> None: self._registry_cache[key] = value
    def get_cached_registry(self, key: str) -> Any: return self._registry_cache.get(key)

    def record_sample(self, name: str, duration_ms: float,
                      metadata: Optional[Dict[str, Any]] = None) -> PerformanceSample:
        sample = PerformanceSample(name=name, duration_ms=duration_ms, metadata=metadata or {})
        self._samples.append(sample)
        return sample

    def get_samples(self) -> list[PerformanceSample]: return list(self._samples)

    def clear_caches(self) -> None:
        self._prompt_cache.clear()
        self._config_cache.clear()
        self._registry_cache.clear()

    def get_timeout_seconds(self) -> float: return self.config.inference_timeout_seconds


# ── LazyLoader (merged from core/lazy_loader.py) ─────────────────────────────

class LazyLoader:
    def __init__(self):
        self._loaded: Dict[str, Any] = {}

    def get_or_load(self, key: str, loader: Callable[[], Any]) -> Any:
        if key not in self._loaded:
            self._loaded[key] = loader()
        return self._loaded[key]

    def is_loaded(self, key: str) -> bool: return key in self._loaded
    def unload(self, key: str) -> None: self._loaded.pop(key, None)
    def clear(self) -> None: self._loaded.clear()
