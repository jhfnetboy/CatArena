"""CatArena module registration + a post-scan hook.

Why a hook is needed
--------------------
GOD's ``scan_and_register_custom_modules(workspace)`` does
``registry.clear_custom_modules()`` and then registers only what it scans from
``<workspace>/custom/{agents,envs}``. It runs at *every* live-session init and
every ``/sync-agents``. So any module CatArena registers programmatically gets
wiped the next time a session initialises.

The fix (no GOD edits): wrap ``scan_and_register_custom_modules`` so that it
re-registers CatArena's modules *after* each clear+scan, and re-bind the wrapped
function everywhere it has already been imported by value
(``agentsociety2.registry``, ``...registry.modules`` and, if already loaded,
``...backend.routers.live_experiments``). Because CatArena's launcher installs
the hook *before* the FastAPI app imports the routers, `from ... import
scan_and_register_custom_modules` inside those routers binds the wrapped version.
"""

from __future__ import annotations

import logging
import sys

from agentsociety2.registry import get_registry

from catarena.envs.beacon_env import CatArenaBeaconEnv

logger = logging.getLogger("catarena.registry")

# registry key -> class. The key MUST match the ``module_type`` used in an
# experiment's ``env_modules`` / ``agents`` entries.
CATARENA_ENV_MODULES: dict = {
    "CatArenaBeaconEnv": CatArenaBeaconEnv,
}
CATARENA_AGENT_MODULES: dict = {
    # "ParticipantAgent": ParticipantAgent,  # M1
}

_HOOK_INSTALLED = False


def register_catarena_modules(registry=None) -> None:
    """(Re)register all CatArena env/agent modules as custom modules.

    We set ``_is_custom = True`` on each class so GOD's introspection treats
    them as first-class custom modules (same as scanned ones). The side effect
    is that ``clear_custom_modules()`` *will* drop them on the next scan — which
    is exactly why :func:`install_registration_hook` re-registers after scans.
    """
    reg = registry or get_registry()
    for name, cls in CATARENA_ENV_MODULES.items():
        cls._is_custom = True
        reg.register_env_module(name, cls, is_custom=True)
    for name, cls in CATARENA_AGENT_MODULES.items():
        cls._is_custom = True
        reg.register_agent_module(name, cls, is_custom=True)
    logger.debug(
        "CatArena modules registered: envs=%s agents=%s",
        list(CATARENA_ENV_MODULES),
        list(CATARENA_AGENT_MODULES),
    )


def install_registration_hook() -> None:
    """Wrap GOD's scan so CatArena modules survive clear+rescan. Idempotent."""
    global _HOOK_INSTALLED
    if _HOOK_INSTALLED:
        return

    import agentsociety2.registry as registry_pkg
    import agentsociety2.registry.modules as registry_modules

    original = registry_modules.scan_and_register_custom_modules

    def wrapped(workspace_path, registry=None):
        result = original(workspace_path, registry)
        register_catarena_modules(registry)
        return result

    wrapped.__wrapped__ = original  # type: ignore[attr-defined]

    # Patch the source module and the package re-export...
    registry_modules.scan_and_register_custom_modules = wrapped
    registry_pkg.scan_and_register_custom_modules = wrapped
    # ...and any consumer that already imported it by value.
    le = sys.modules.get("agentsociety2.backend.routers.live_experiments")
    if le is not None and hasattr(le, "scan_and_register_custom_modules"):
        le.scan_and_register_custom_modules = wrapped

    # Register once now, so our modules exist even before the first scan.
    register_catarena_modules()

    _HOOK_INSTALLED = True
    logger.info("CatArena registration hook installed")
