"""CatArena backend launcher.

Installs the CatArena registration hook, then starts the GOD (agentsociety2)
FastAPI backend *in-process*. GOD is used as a library; no submodule files are
edited. Because uvicorn runs with ``reload=False`` (no subprocess) and the hook
is installed before the app string is imported, the router's
``from ...registry import scan_and_register_custom_modules`` binds the wrapped
version.

Env vars (same as GOD's backend): BACKEND_HOST, BACKEND_PORT, BACKEND_LOG_LEVEL,
plus the AGENTSOCIETY_LLM_* / LIVE_WORKSPACE_PATH set by scripts/catarena.sh.
"""

from __future__ import annotations

import os


def main() -> None:
    from catarena.registry import install_registration_hook

    install_registration_hook()

    import uvicorn

    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8011"))
    log_level = os.getenv("BACKEND_LOG_LEVEL", "info")

    print(f"[CatArena] backend on http://{host}:{port} (GOD engine, hook installed)")
    uvicorn.run(
        "agentsociety2.backend.app:app",
        host=host,
        port=port,
        reload=False,
        log_level=log_level,
        ws="wsproto",
    )


if __name__ == "__main__":
    main()
