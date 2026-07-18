#!/usr/bin/env bash

# One-command metadata RAG rollout for the Ubuntu/WSL development environment.
# Usage:
#   bash scripts/rollout_mvp.sh
#   bash scripts/rollout_mvp.sh mvp-metadata-v2

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

INDEX_VERSION="${1:-mvp-metadata-v1}"
PYTHON="${PROJECT_ROOT}/wsl_venv/bin/python"
ENV_FILE="${PROJECT_ROOT}/.env"
COLLECTION_NAME="ctu_scholarship_docs_${INDEX_VERSION}"
ALIAS_NAME="ctu_scholarship_docs_current"
LEGACY_COLLECTION="ctu_scholarship_docs_v3"
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
ACTIVATED=0
COMPOSE=()

log() {
    printf '\n[MVP] %s\n' "$*"
}

die() {
    printf '\n[MVP] ERROR: %s\n' "$*" >&2
    exit 1
}

set_metadata_filter() {
    local value="$1"
    if grep -q '^RAG_METADATA_FILTER_ENABLED=' "${ENV_FILE}"; then
        sed -i "s/^RAG_METADATA_FILTER_ENABLED=.*/RAG_METADATA_FILTER_ENABLED=${value}/" "${ENV_FILE}"
    else
        printf '\nRAG_METADATA_FILTER_ENABLED=%s\n' "${value}" >> "${ENV_FILE}"
    fi

    if grep -q '^QDRANT_COLLECTION_ALIAS=' "${ENV_FILE}"; then
        sed -i "s/^QDRANT_COLLECTION_ALIAS=.*/QDRANT_COLLECTION_ALIAS=${ALIAS_NAME}/" "${ENV_FILE}"
    else
        printf 'QDRANT_COLLECTION_ALIAS=%s\n' "${ALIAS_NAME}" >> "${ENV_FILE}"
    fi
}

rollback_on_error() {
    local exit_code=$?
    trap - ERR
    set +e

    printf '\n[MVP] Rollout failed (exit %s). Metadata filter remains disabled.\n' "${exit_code}" >&2
    set_metadata_filter false

    if [[ "${ACTIVATED}" == "1" ]]; then
        printf '[MVP] Moving alias back to %s...\n' "${LEGACY_COLLECTION}" >&2
        "${PYTHON}" scripts/reindex_all.py activate \
            --collection "${LEGACY_COLLECTION}" \
            --allow-unvalidated
    fi

    printf '[MVP] No Gemini request was made. Fix the error above, then rerun with a new version if needed, for example:\n' >&2
    printf '      bash scripts/rollout_mvp.sh mvp-metadata-v2\n' >&2
    exit "${exit_code}"
}

trap rollback_on_error ERR

[[ -x "${PYTHON}" ]] || die "Missing executable ${PYTHON}. Run this script inside Ubuntu WSL with wsl_venv available."
[[ -f "${ENV_FILE}" ]] || die "Missing ${ENV_FILE}."
[[ "${INDEX_VERSION}" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$ ]] \
    || die "Invalid index version '${INDEX_VERSION}'. Use only letters, digits, underscore and dash."
command -v docker >/dev/null 2>&1 || die "Docker is not available inside this WSL terminal."
command -v curl >/dev/null 2>&1 || die "curl is required."

if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE=(docker-compose)
else
    die "Docker Compose is not available."
fi

if { command -v ss >/dev/null 2>&1 && ss -ltnH | grep -q ':8000[[:space:]]'; } \
    || curl --silent --fail --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1; then
    die "Port 8000 is serving the old app. Stop it with Ctrl+C, then run this script again."
fi

log "Starting Qdrant, Redis and PostgreSQL"
"${COMPOSE[@]}" up -d qdrant redis postgres

log "Waiting for Qdrant"
for _ in {1..30}; do
    if curl --silent --fail --max-time 2 "${QDRANT_URL}/" >/dev/null 2>&1; then
        break
    fi
    sleep 2
done
curl --silent --fail --max-time 5 "${QDRANT_URL}/" >/dev/null \
    || die "Qdrant did not become ready at ${QDRANT_URL}."

log "Waiting for Redis and PostgreSQL"
for _ in {1..30}; do
    if "${COMPOSE[@]}" exec -T redis redis-cli ping 2>/dev/null | grep -q '^PONG$' \
        && "${COMPOSE[@]}" exec -T postgres pg_isready -U admin -d ctu_chatbot >/dev/null 2>&1; then
        break
    fi
    sleep 2
done
"${COMPOSE[@]}" exec -T redis redis-cli ping | grep -q '^PONG$' \
    || die "Redis did not become ready."
"${COMPOSE[@]}" exec -T postgres pg_isready -U admin -d ctu_chatbot >/dev/null \
    || die "PostgreSQL did not become ready."

# The running application must never use metadata filters until the new
# collection has passed both structural validation and retrieval assertions.
set_metadata_filter false

log "Preflight: validating UTF-8 and the 46-document metadata catalog"
"${PYTHON}" scripts/reindex_all.py preflight

if curl --silent --fail --max-time 5 \
    "${QDRANT_URL}/collections/${COLLECTION_NAME}" >/dev/null 2>&1; then
    log "Collection ${COLLECTION_NAME} already exists; skipping build and validating it"
else
    log "Building ${COLLECTION_NAME}. This is the slow embedding step"
    "${PYTHON}" scripts/reindex_all.py build --index-version "${INDEX_VERSION}"
fi

log "Validating vectors, metadata, checksums and Qdrant-to-PostgreSQL links"
"${PYTHON}" scripts/reindex_all.py validate --index-version "${INDEX_VERSION}"

log "Activating ${COLLECTION_NAME} through ${ALIAS_NAME}"
"${PYTHON}" scripts/reindex_all.py activate --index-version "${INDEX_VERSION}"
ACTIVATED=1

log "Running retrieval-only acceptance tests (no Gemini/Groq calls)"
"${PYTHON}" scripts/test_retriever.py

log "All retrieval tests passed; enabling metadata filters"
set_metadata_filter true
ACTIVATED=0
trap - ERR

log "MVP is ready. Starting FastAPI on http://localhost:8000"
log "Keep this terminal open; stop the app later with Ctrl+C"
exec "${PYTHON}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
