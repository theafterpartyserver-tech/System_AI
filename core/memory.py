from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryScope(str, Enum):
    EPHEMERAL = "ephemeral"
    SESSION = "session"
    LONG_TERM = "long_term"


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    TASK = "task"
    TOOL_RESULT = "tool_result"
    SKILL = "skill"
    ERROR = "error"
    SUMMARY = "summary"
    CUSTOM = "custom"


@dataclass
class MemoryItem:
    id: str
    text: str
    scope: MemoryScope
    memory_type: MemoryType = MemoryType.CUSTOM
    topic: Optional[str] = None
    tool_usage: Optional[str] = None
    skill_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0
    expires_at: Optional[float] = None
    pinned: bool = False
    confidence: float = 1.0
    version: int = 1


@dataclass
class MemoryQuery:
    text: str
    scope: Optional[MemoryScope] = None
    memory_type: Optional[MemoryType] = None
    topic: Optional[str] = None
    tool_usage: Optional[str] = None
    skill_name: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    exact_phrase: Optional[str] = None
    semantic_hint: Optional[str] = None
    limit: int = 10
    include_expired: bool = False


@dataclass
class MemoryRetrievalResult:
    items: List[MemoryItem] = field(default_factory=list)
    matched_ids: List[str] = field(default_factory=list)
    excluded_ids: List[str] = field(default_factory=list)
    debug: Dict[str, Any] = field(default_factory=dict)

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

class MemoryPersistenceManager:
        
    def __init__(self, memory_dir: Path = None, index_path: Path = None):
        self.memory_dir = memory_dir or Path('./memory')
        self.index_path = index_path or self.memory_dir / 'index.json'
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and 'entries' in loaded:
                        return loaded
            except:
                pass
        return {"entries": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def save_memory(self, key: str, data: Any, metadata: Dict = None) -> bool:
        try:
            file_path = self.memory_dir / f"{key}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            if not isinstance(self.index, dict):
                self.index = {"entries": [], "metadata": {}}
            if "entries" not in self.index:
                self.index["entries"] = []
            
            existing = [e for e in self.index["entries"] if e["key"] == key]
            if existing:
                self.index["entries"].remove(existing[0])
            
            self.index["entries"].append({
                "key": key,
                "file": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })
            self._save_index()
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def load_memory(self, key: str) -> Any:
        try:
            file_path = self.memory_dir / f"{key}.json"
            if file_path.exists():
                with open(file_path) as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
        return None
    
    def list_memory(self) -> List[str]:
        if isinstance(self.index, dict) and "entries" in self.index:
            return [e["key"] for e in self.index["entries"]]
        return []
    
    def clear_memory(self, key: str) -> bool:
        try:
            file_path = self.memory_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
            if not isinstance(self.index, dict):
                self.index = {"entries": [], "metadata": {}}
            if "entries" not in self.index:
                self.index["entries"] = []
            self.index["entries"] = [e for e in self.index["entries"] if e["key"] != key]
            self._save_index()
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def get_stats(self) -> dict:
        try:
            total_size = 0
            for f in self.memory_dir.glob("*.json"):
                if f.name != "index.json":
                    total_size += f.stat().st_size
        except:
            total_size = 0
        return {
            "entries": len(self.list_memory()),
            "total_size_bytes": total_size,
            "created": self.index.get("metadata", {}).get("created"),
        }
    
    def _save_index(self):
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")

from pathlib import Path
import json
import gzip
from datetime import datetime
from typing import List, Dict, Any, Optional


class MemoryIndex:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index: Dict[str, Any] = {}
        if self.index_path.exists():
            try:
                self.index = json.loads(self.index_path.read_text(encoding="utf-8"))
            except Exception:
                self.index = {}

    def add_entry(self, key: str, data: Dict[str, Any]) -> None:
        self.index[key] = data
        self._save()

    def get_entry(self, key: str) -> Optional[Dict[str, Any]]:
        return self.index.get(key)

    def _save(self) -> None:
        self.index_path.write_text(json.dumps(self.index, indent=2), encoding="utf-8")


class MemoryCompressor:
    def __init__(self, memory_dir: Path, logs_dir: Path, index_path: Path, interval_turns: int = 100):
        self.memory_dir = memory_dir
        self.logs_dir = logs_dir
        self.index_path = index_path
        self.interval_turns = interval_turns
        self.turn_counter = 0
        self.index = MemoryIndex(index_path)

    def _compress_file(self, src: Path, dest: Path) -> None:
        if not src.exists():
            return
        with open(src, "rb") as f_in:
            with gzip.open(dest.with_suffix(dest.suffix + ".gz"), "wb") as f_out:
                f_out.write(f_in.read())
        src.unlink(missing_ok=True)

    def record_turn(self) -> None:
        self.turn_counter += 1
        if self.turn_counter % self.interval_turns != 0:
            return

        self.index.add_entry(
            f"last_compression_turn",
            {"turn": self.turn_counter, "timestamp": datetime.utcnow().isoformat()}
        )

        memory_files = list(self.memory_dir.glob("*.jsonl"))
        for f in memory_files:
            compressed = self.memory_dir / f.name
            self._compress_file(f, compressed)

        logs_files = list(self.logs_dir.glob("*.log"))
        for f in logs_files:
            compressed = self.logs_dir / f.name
            self._compress_file(f, compressed)

        print(f"Compressed {len(memory_files) + len(logs_files)} files at turn {self.turn_counter}.")

    def add_context_entry(self, turn_id: str, path: str, offset: int, length: int) -> None:
        self.index.add_entry(
            f"context:{turn_id}",
            {
                "path": path,
                "offset": offset,
                "length": length,
            }
        )

import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# models defined above


class MemoryManager:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self._ephemeral: List[MemoryItem] = []
        self._session: List[MemoryItem] = []
        self._long_term: List[MemoryItem] = []
        self._retrieval_log: List[Dict[str, Any]] = []

    def add_memory(
        self,
        text: str,
        scope: MemoryScope = MemoryScope.SESSION,
        memory_type: MemoryType = MemoryType.CUSTOM,
        topic: Optional[str] = None,
        tool_usage: Optional[str] = None,
        skill_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[float] = None,
        pinned: bool = False,
        confidence: float = 1.0,
    ) -> MemoryItem:
        now = time.time()
        item = MemoryItem(
            id=str(uuid.uuid4()),
            text=text.strip(),
            scope=scope,
            memory_type=memory_type,
            topic=topic,
            tool_usage=tool_usage,
            skill_name=skill_name,
            tags=tags or [],
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            pinned=pinned,
            confidence=confidence,
            version=1,
        )
        self._bucket_for_scope(scope).append(item)
        return item

    def add_ephemeral(self, text: str, **kwargs: Any) -> MemoryItem:
        return self.add_memory(text=text, scope=MemoryScope.EPHEMERAL, **kwargs)

    def add_session(self, text: str, **kwargs: Any) -> MemoryItem:
        return self.add_memory(text=text, scope=MemoryScope.SESSION, **kwargs)

    def add_long_term(self, text: str, **kwargs: Any) -> MemoryItem:
        return self.add_memory(text=text, scope=MemoryScope.LONG_TERM, **kwargs)

    def deduplicate(self) -> int:
        removed = 0
        for bucket_name in ("_ephemeral", "_session", "_long_term"):
            bucket = getattr(self, bucket_name)
            seen = set()
            deduped = []
            for item in bucket:
                key = self._normalize_text(item.text)
                if key in seen and not item.pinned:
                    removed += 1
                    continue
                seen.add(key)
                deduped.append(item)
            setattr(self, bucket_name, deduped)
        return removed

    def compress_session(self, max_items: int = 50) -> Optional[MemoryItem]:
        if len(self._session) <= max_items:
            return None

        text = self._build_summary_text(self._session)
        summary = self.add_long_term(
            text=text,
            memory_type=MemoryType.SUMMARY,
            topic="session_summary",
            metadata={"source": "compress_session"},
            pinned=True,
        )
        self._session = self._session[-max_items:]
        return summary

    def retrieve(self, query: MemoryQuery) -> MemoryRetrievalResult:
        candidates = list(self._iter_candidates(query.include_expired))
        matched: List[MemoryItem] = []
        excluded: List[str] = []
        debug: Dict[str, Any] = {"scores": {}}

        for item in candidates:
            if not self._matches_filters(item, query):
                excluded.append(item.id)
                continue

            score = self._score_item(item, query)
            if score <= 0:
                excluded.append(item.id)
                continue

            debug["scores"][item.id] = score
            matched.append(item)

        matched.sort(key=lambda x: self._score_item(x, query), reverse=True)
        matched = matched[: query.limit]

        result = MemoryRetrievalResult(
            items=matched,
            matched_ids=[item.id for item in matched],
            excluded_ids=excluded,
            debug=debug,
        )
        self._log_retrieval(query, result)
        return result

    def lookup_keyword(self, keywords: Iterable[str], limit: int = 10) -> MemoryRetrievalResult:
        return self.retrieve(
            MemoryQuery(text=" ".join(keywords), keywords=list(keywords), limit=limit)
        )

    def lookup_phrase(self, phrase: str, limit: int = 10) -> MemoryRetrievalResult:
        return self.retrieve(
            MemoryQuery(text=phrase, exact_phrase=phrase, limit=limit)
        )

    def lookup_semantic(self, hint: str, limit: int = 10) -> MemoryRetrievalResult:
        return self.retrieve(
            MemoryQuery(text=hint, semantic_hint=hint, limit=limit)
        )

    def summarize_if_needed(self) -> Optional[MemoryItem]:
        return self.compress_session()

    def clear_ephemeral(self) -> None:
        self._ephemeral.clear()

    def clear_session(self) -> None:
        self._session.clear()

    def clear_long_term(self) -> None:
        self._long_term.clear()

    def export_memory(self) -> Dict[str, Any]:
        return {
            "ephemeral": [asdict(item) for item in self._ephemeral],
            "session": [asdict(item) for item in self._session],
            "long_term": [asdict(item) for item in self._long_term],
        }

    def import_memory(self, payload: Dict[str, Any]) -> None:
        self._ephemeral = self._load_items(payload.get("ephemeral", []))
        self._session = self._load_items(payload.get("session", []))
        self._long_term = self._load_items(payload.get("long_term", []))

    def _bucket_for_scope(self, scope: MemoryScope) -> List[MemoryItem]:
        if scope == MemoryScope.EPHEMERAL:
            return self._ephemeral
        if scope == MemoryScope.SESSION:
            return self._session
        return self._long_term

    def _iter_candidates(self, include_expired: bool) -> Iterable[MemoryItem]:
        for bucket in (self._ephemeral, self._session, self._long_term):
            for item in bucket:
                if not include_expired and self._is_expired(item):
                    continue
                yield item

    def _matches_filters(self, item: MemoryItem, query: MemoryQuery) -> bool:
        if query.scope and item.scope != query.scope:
            return False
        if query.memory_type and item.memory_type != query.memory_type:
            return False
        if query.topic and item.topic != query.topic:
            return False
        if query.tool_usage and item.tool_usage != query.tool_usage:
            return False
        if query.skill_name and item.skill_name != query.skill_name:
            return False
        return True

    def _score_item(self, item: MemoryItem, query: MemoryQuery) -> float:
        score = 0.0
        item_text = self._normalize_text(item.text)
        qtext = self._normalize_text(query.text)

        if query.exact_phrase and query.exact_phrase in item.text:
            score += 10.0
        if query.keywords:
            for kw in query.keywords:
                if self._normalize_text(kw) in item_text:
                    score += 2.0
        if qtext and qtext in item_text:
            score += 3.0
        if query.semantic_hint and query.semantic_hint.lower() in item_text:
            score += 1.5
        if item.topic and query.topic and item.topic == query.topic:
            score += 2.0
        if item.tool_usage and query.tool_usage and item.tool_usage == query.tool_usage:
            score += 2.0
        if item.skill_name and query.skill_name and item.skill_name == query.skill_name:
            score += 2.0

        score += min(item.confidence, 1.0)
        if item.pinned:
            score += 1.0
        score += max(0.0, 1.0 - ((time.time() - item.updated_at) / 100000.0))
        return score

    def _log_retrieval(self, query: MemoryQuery, result: MemoryRetrievalResult) -> None:
        self._retrieval_log.append(
            {
                "query": query.text,
                "scope": query.scope.value if query.scope else None,
                "memory_type": query.memory_type.value if query.memory_type else None,
                "topic": query.topic,
                "tool_usage": query.tool_usage,
                "skill_name": query.skill_name,
                "matched_ids": result.matched_ids,
                "excluded_ids": result.excluded_ids,
                "timestamp": time.time(),
            }
        )

    def _is_expired(self, item: MemoryItem) -> bool:
        return item.expires_at is not None and time.time() >= item.expires_at

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.lower().split())

    def _build_summary_text(self, items: List[MemoryItem]) -> str:
        parts = [item.text for item in items if item.text]
        return " | ".join(parts[-20:])

    def _load_items(self, items: List[Dict[str, Any]]) -> List[MemoryItem]:
        loaded: List[MemoryItem] = []
        for raw in items:
            loaded.append(
                MemoryItem(
                    id=raw.get("id", str(uuid.uuid4())),
                    text=raw.get("text", ""),
                    scope=MemoryScope(raw.get("scope", "session")),
                    memory_type=MemoryType(raw.get("memory_type", "custom")),
                    topic=raw.get("topic"),
                    tool_usage=raw.get("tool_usage"),
                    skill_name=raw.get("skill_name"),
                    tags=list(raw.get("tags", [])),
                    metadata=dict(raw.get("metadata", {})),
                    created_at=float(raw.get("created_at", 0.0)),
                    updated_at=float(raw.get("updated_at", 0.0)),
                    expires_at=raw.get("expires_at"),
                    pinned=bool(raw.get("pinned", False)),
                    confidence=float(raw.get("confidence", 1.0)),
                    version=int(raw.get("version", 1)),
                )
            )
        return loaded