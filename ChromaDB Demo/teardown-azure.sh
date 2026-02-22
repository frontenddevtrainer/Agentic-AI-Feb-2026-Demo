#!/usr/bin/env bash
# =============================================================================
# teardown-azure.sh  –  Delete ALL Azure resources created by deploy-azure.sh
#
# Deletes the entire resource group (ACR + ACI container group) in one shot.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_FILE="$SCRIPT_DIR/.azure-deploy-state"

# ── Load saved state or fall back to defaults ─────────────────────────────────
if [ -f "$STATE_FILE" ]; then
  source "$STATE_FILE"
else
  RESOURCE_GROUP="chromadb-demo-rg"
  echo "Note: state file not found – using default resource group '$RESOURCE_GROUP'."
fi

# ── Confirm ───────────────────────────────────────────────────────────────────
echo ""
echo "WARNING: This will permanently delete resource group '$RESOURCE_GROUP'"
echo "         and EVERYTHING inside it (ACR, container group, public IP)."
echo ""
read -rp "Type the resource group name to confirm: " CONFIRM

if [ "$CONFIRM" != "$RESOURCE_GROUP" ]; then
  echo "Input did not match. Aborting."
  exit 1
fi

# ── Delete ────────────────────────────────────────────────────────────────────
echo ""
echo "▶ Deleting resource group '$RESOURCE_GROUP'..."
az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait

echo ""
echo "✔ Deletion initiated. Azure will finish removing resources in ~1-2 minutes."
echo "  Verify at: https://portal.azure.com → Resource groups"
echo ""

# Clean up local state
rm -f "$STATE_FILE"
echo "✔ Local state file removed."
