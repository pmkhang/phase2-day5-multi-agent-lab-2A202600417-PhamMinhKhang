"""Tracing hooks with Langfuse v4 integration.

Env vars (LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST) must be set
before the first call to get_client(). Call init_tracing() early in app startup.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

_ready = False


def init_tracing() -> None:
    """Set Langfuse env vars from app settings. Call once at startup."""
    global _ready
    if _ready:
        return
    try:
        from multi_agent_research_lab.core.config import get_settings
        s = get_settings()
        if s.langfuse_secret_key:
            os.environ.setdefault("LANGFUSE_SECRET_KEY", s.langfuse_secret_key)
        if s.langfuse_public_key:
            os.environ.setdefault("LANGFUSE_PUBLIC_KEY", s.langfuse_public_key)
        os.environ.setdefault("LANGFUSE_HOST", s.langfuse_base_url)
    except Exception:
        pass
    _ready = True


def _get_langfuse() -> Any:
    init_tracing()
    try:
        from langfuse import get_client
        lf = get_client()
        if lf.auth_check():
            return lf
    except Exception:
        pass
    return None


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Yield a mutable span dict; sends span to Langfuse v4 if configured."""
    started = perf_counter()
    span: dict[str, Any] = {
        "name": name,
        "attributes": attributes or {},
        "duration_seconds": None,
        "status": "ok",
        "error": None,
    }

    attrs = attributes or {}
    run_id = str(attrs.get("run_id", ""))
    lf = _get_langfuse()
    lf_span = None

    if lf is not None and len(run_id) == 32:
        try:
            from langfuse.types import TraceContext
            lf_span = lf.start_observation(
                trace_context=TraceContext(trace_id=run_id),
                name=name,
                as_type="span",
                input=attrs,
            )
        except Exception:
            lf_span = None

    try:
        yield span
    except Exception as exc:
        span["status"] = "error"
        span["error"] = str(exc)
        raise
    finally:
        span["duration_seconds"] = perf_counter() - started
        if lf_span is not None:
            try:
                lf_span.update(
                    output={"status": span["status"], "duration_s": span["duration_seconds"]}
                )
                lf_span.end()
            except Exception:
                pass


def flush_trace(run_id: str, query: str = "") -> None:
    """Flush pending Langfuse events and set trace name."""
    lf = _get_langfuse()
    if lf is not None:
        try:
            lf.flush()
        except Exception:
            pass
        # POST after flush to set trace name (SDK v4 overrides name with last span)
        if len(run_id) == 32:
            try:
                import base64
                import json
                import urllib.request
                from multi_agent_research_lab.core.config import get_settings
                s = get_settings()
                creds = base64.b64encode(
                    f"{s.langfuse_public_key}:{s.langfuse_secret_key}".encode()
                ).decode()
                payload = json.dumps({"id": run_id, "name": "multi-agent-run"}).encode()
                req = urllib.request.Request(
                    f"{s.langfuse_base_url}/api/public/traces",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Basic {creds}"},
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
