#!/usr/bin/env bash
# CatArena launcher (M0).
#
# Uses the GOD submodule purely as a library: CatArena code is put on PYTHONPATH
# and run with GOD's own venv (which already has agentsociety2 + deps). No GOD
# source is edited; GOD's venv is only *used*, not modified.
#
#   catarena.sh verify    # prove the extension seam (no server/runtime needed)
#   catarena.sh backend   # start the CatArena backend (GOD engine + hook) on :8011
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOD_DIR="$ROOT_DIR/GOD"
BACKEND_ROOT="$GOD_DIR/agentsociety"
VENV_PY="$BACKEND_ROOT/.venv/bin/python"
ENV_FILE="$GOD_DIR/.env"

if [[ ! -x "$VENV_PY" ]]; then
  echo "[CatArena] GOD venv not found at $VENV_PY" >&2
  echo "           run: (cd $GOD_DIR && ./scripts/god.sh setup)" >&2
  exit 1
fi

cmd="${1:-verify}"
case "$cmd" in
  verify)
    echo "[CatArena] M0 seam proof — GOD used as a library, no submodule edits"
    PYTHONPATH="$ROOT_DIR" exec "$VENV_PY" -m catarena.verify_seam
    ;;

  backend)
    # Reuse GOD's model config; run on an alt port so it can coexist with a
    # running GOD backend (8001).
    set -a
    # shellcheck disable=SC1090
    [[ -f "$ENV_FILE" ]] && source "$ENV_FILE"
    set +a
    export AGENTSOCIETY_LLM_API_KEY="${GOD_LLM_API_KEY:-}"
    export AGENTSOCIETY_LLM_API_BASE="${GOD_LLM_API_BASE:-https://api.openai.com/v1}"
    export AGENTSOCIETY_LLM_MODEL="${GOD_LLM_MODEL:-}"
    export AGENTSOCIETY_NANO_LLM_MODEL="${GOD_LLM_NANO_MODEL:-${GOD_LLM_MODEL:-}}"
    export AGENTSOCIETY_EMBEDDING_API_KEY="${GOD_EMBEDDING_API_KEY:-$AGENTSOCIETY_LLM_API_KEY}"
    export AGENTSOCIETY_EMBEDDING_API_BASE="${GOD_EMBEDDING_API_BASE:-$AGENTSOCIETY_LLM_API_BASE}"
    export AGENTSOCIETY_EMBEDDING_MODEL="${GOD_EMBEDDING_MODEL:-text-embedding-3-large}"
    export LIVE_WORKSPACE_PATH="${LIVE_WORKSPACE_PATH:-$BACKEND_ROOT/quick_experiments}"
    export BACKEND_HOST="${CATARENA_BACKEND_HOST:-127.0.0.1}"
    export BACKEND_PORT="${CATARENA_BACKEND_PORT:-8011}"
    export BACKEND_LOG_LEVEL="${BACKEND_LOG_LEVEL:-info}"
    echo "[CatArena] backend http://$BACKEND_HOST:$BACKEND_PORT  workspace=$LIVE_WORKSPACE_PATH"
    cd "$BACKEND_ROOT"
    PYTHONPATH="$ROOT_DIR" exec "$VENV_PY" -m catarena.run
    ;;

  *)
    echo "usage: catarena.sh {verify|backend}" >&2
    exit 2
    ;;
esac
