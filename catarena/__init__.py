"""CatArena — a multi-user agent arena built on top of the GOD engine.

GOD (the `GOD/` submodule) is used as a *library* and kept pristine: CatArena
never edits GOD source. Custom behaviour is layered in via programmatic
registration + a post-scan hook (see :mod:`catarena.registry`), extra env
modules, and sidecar services.
"""

__version__ = "0.0.0"
