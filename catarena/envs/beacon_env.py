"""CatArenaBeaconEnv — a minimal no-op env module.

M0 uses it as a proof-of-life for the extension seam: a CatArena-provided env
module that (a) is registered programmatically rather than scanned from GOD's
``custom/`` dir, (b) survives GOD's clear+rescan at session init, and (c) can be
listed as a second entry in an experiment's ``env_modules`` and participate in
the per-step loop — all without editing the GOD submodule.

Later milestones replace/extend this with real modules (DirectMessageEnv,
BulletinBoardEnv).
"""

from __future__ import annotations

from datetime import datetime

from agentsociety2.env.base import EnvBase


class CatArenaBeaconEnv(EnvBase):
    """A harmless env that only counts simulation ticks.

    Declares no state columns, so it creates no replay tables and cannot
    interfere with the town. ``step`` must be overridden — the base raises
    ``NotImplementedError``.
    """

    def __init__(self) -> None:
        super().__init__()
        self._ticks = 0

    async def step(self, tick: int, t: datetime):  # noqa: D401 - see base
        self._ticks += 1
        return None

    # ---- optional persistence hooks ----
    def _dump_state(self) -> dict:
        return {"ticks": self._ticks}

    def _load_state(self, state: dict) -> None:
        if isinstance(state, dict):
            self._ticks = int(state.get("ticks", 0))
