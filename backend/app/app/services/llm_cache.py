from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT_DIR / "tmp"
CACHE_DB = CACHE_DIR / "llm_response_cache.sqlite3"


class LLMCache:
    _memory_cache: dict[str, str] = {}
    _memory_hits: int = 0

    def __init__(self, db_path: Path = CACHE_DB) -> None:
        self.db_path = db_path

    def is_enabled(self) -> bool:
        return os.getenv("LLM_CACHE_DISABLED", "").strip().lower() not in {"1", "true", "yes"}

    def build_key(
        self,
        *,
        provider: str,
        model: str,
        base_url: str,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> str:
        raw = json.dumps(
            {
                "provider": provider,
                "model": model,
                "base_url": base_url,
                "messages": messages,
                "temperature": temperature,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> str | None:
        if not self.is_enabled():
            return None
        if key in self._memory_cache:
            type(self)._memory_hits += 1
            return self._memory_cache[key]
        try:
            self._ensure_schema()
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("select response_text from llm_cache where cache_key = ?", (key,)).fetchone()
                if row is None:
                    return None
                conn.execute(
                    "update llm_cache set hit_count = hit_count + 1, last_hit_at = ? where cache_key = ?",
                    (int(time.time()), key),
                )
                value = str(row[0])
                self._memory_cache[key] = value
                return value
        except sqlite3.Error:
            return None

    def set(self, key: str, response_text: str, metadata: dict[str, Any]) -> None:
        if not self.is_enabled():
            return
        self._memory_cache[key] = response_text
        now = int(time.time())
        metadata_text = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        try:
            self._ensure_schema()
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    insert into llm_cache(cache_key, response_text, metadata, created_at, last_hit_at, hit_count)
                    values(?, ?, ?, ?, ?, 0)
                    on conflict(cache_key) do update set
                        response_text = excluded.response_text,
                        metadata = excluded.metadata,
                        last_hit_at = excluded.last_hit_at
                    """,
                    (key, response_text, metadata_text, now, now),
                )
        except sqlite3.Error:
            return

    def stats(self) -> dict[str, int | str]:
        try:
            self._ensure_schema()
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("select count(*), coalesce(sum(hit_count), 0) from llm_cache").fetchone()
            return {
                "enabled": "true" if self.is_enabled() else "false",
                "backend": "sqlite",
                "entries": int(row[0]),
                "hits": int(row[1]),
                "path": str(self.db_path),
            }
        except sqlite3.Error as exc:
            return {
                "enabled": "true" if self.is_enabled() else "false",
                "backend": "memory",
                "entries": len(self._memory_cache),
                "hits": self._memory_hits,
                "path": str(self.db_path),
                "warning": str(exc),
            }

    def _ensure_schema(self) -> None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                create table if not exists llm_cache (
                    cache_key text primary key,
                    response_text text not null,
                    metadata text not null,
                    created_at integer not null,
                    last_hit_at integer not null,
                    hit_count integer not null default 0
                )
                """
            )
