#!/usr/bin/env bash
# Baseline (task only) vs candidate (skill body + named reference appended to the system prompt).
# Tools, skills, MCP and user settings are disabled in both arms; run from an empty directory.
set -u
REPO="$(cd "$(dirname "$0")/../../../.." && pwd)"
OUT="$REPO/docs/evidence/verification/2026-09-28-probes"
S="$REPO/plugins/web3d-dev/skills"
EMPTY="$(mktemp -d)"
q() { python3 -c "import json,sys;print([s for s in json.load(open('$REPO/test/evals/scenarios.json'))['scenarios'] if s['id']=='$1'][0]['query'])"; }
arm() { # id arm files...
  local id=$1 arm=$2; shift 2
  local sys=""; for f in "$@"; do sys+=$'\n\n'"$(cat "$f")"; done
  ( cd "$EMPTY" && if [ -z "$sys" ]; then
      claude -p "$(q "$id")" --tools "" --disable-slash-commands --strict-mcp-config --setting-sources ""
    else
      claude -p "$(q "$id")" --tools "" --disable-slash-commands --strict-mcp-config --setting-sources "" --append-system-prompt "$sys"
    fi ) > "$OUT/$id-$arm.md" 2>&1
}
arm s01 candidate "$S/web3d-runtime/SKILL.md" "$S/web3d-runtime/references/tsl-and-compute.md" &
arm s02 candidate "$S/web3d-animation/SKILL.md" "$S/web3d-animation/references/runtime-patterns.md" &
arm s03 candidate "$S/web3d-assets/SKILL.md" "$S/web3d-assets/references/gltf-pipeline.md" &
wait
rm -rf "$EMPTY"
echo done
