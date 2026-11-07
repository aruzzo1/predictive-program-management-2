"""Logging helpers and the retrieval-trace writer."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def write_retrieval_trace(trace: dict, out_dir: Path) -> Path:
    """Save a trace (query, retrieved chunks, prompt, answer, verifier report) as timestamped JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path
