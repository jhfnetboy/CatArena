"""M0 seam proof (no server, no runtime required).

Proves the extension mechanism end-to-end against the real GOD engine:

1. THREAT  — register a CatArena module, then run GOD's *unwrapped* scan of the
   GOD ``custom/`` dir. GOD's ``clear_custom_modules()`` wipes ours, confirming
   the problem is real.
2. FIX     — install the CatArena hook, scan again. Now GOD's own modules
   (``PixelTownSocialEnv``, ``JiuwenClawAgent``) *and* CatArena's
   ``CatArenaBeaconEnv`` are all registered together.

Exit 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

from pathlib import Path


def _god_workspace() -> Path:
    root = Path(__file__).resolve().parents[1]
    ws = root / "GOD" / "agentsociety"
    if not (ws / "custom").is_dir():
        raise SystemExit(f"GOD custom/ dir not found under {ws} — is the submodule checked out?")
    return ws


def main() -> int:
    god_ws = _god_workspace()

    import agentsociety2.registry as registry_pkg
    import agentsociety2.registry.modules as registry_modules
    from agentsociety2.registry import get_registry

    from catarena.registry import install_registration_hook, register_catarena_modules

    reg = get_registry()

    # 1) THREAT: our module is cleared by GOD's plain (unwrapped) scan.
    register_catarena_modules(reg)
    assert "CatArenaBeaconEnv" in dict(reg.list_env_modules()), "precondition: beacon registered"
    registry_modules.scan_and_register_custom_modules(god_ws)  # original, unwrapped
    threat_wiped = "CatArenaBeaconEnv" not in dict(reg.list_env_modules())

    # 2) FIX: install hook, scan again -> ours survives alongside GOD's.
    install_registration_hook()
    registry_pkg.scan_and_register_custom_modules(god_ws)  # now wrapped

    envs = dict(reg.list_env_modules())
    agents = dict(reg.list_agent_modules())

    checks = {
        "THREAT confirmed: plain GOD scan wipes CatArena module": threat_wiped,
        "GOD env  PixelTownSocialEnv registered": "PixelTownSocialEnv" in envs,
        "GOD agent JiuwenClawAgent registered": "JiuwenClawAgent" in agents,
        "FIX: CatArenaBeaconEnv survives GOD rescan": "CatArenaBeaconEnv" in envs,
    }
    ok = all(checks.values())
    for label, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {label}")
    print(f"\nregistered env modules  : {sorted(envs)}")
    print(f"registered agent modules: {sorted(agents)}")
    print("\nM0 SEAM:", "PASS ✅" if ok else "FAIL ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
