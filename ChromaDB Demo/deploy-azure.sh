#!/usr/bin/env bash
# =============================================================================
# deploy-azure.sh  –  Deploy ChromaDB Demo to Azure Container Instances
#
# Cost profile (minimum):
#   ACR Basic   ~$0.17 / day
#   ACI (2 containers, 0.5 vCPU + 1 GB each)  ~$0.07 / hour
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Resource names ────────────────────────────────────────────────────────────
SUFFIX="$(date +%s | tail -c 7)"          # 7-digit timestamp suffix
RESOURCE_GROUP="chromadb-demo-rg"
LOCATION="eastus"
ACR_NAME="chromadbdemo${SUFFIX}"           # globally unique, alphanumeric only
CONTAINER_GROUP="chromadb-demo"
DNS_LABEL="chromadb-demo-${SUFFIX}"

STATE_FILE="$SCRIPT_DIR/.azure-deploy-state"

# ── Load .env ─────────────────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "ERROR: .env file not found at $SCRIPT_DIR/.env"
  echo "Copy .env.example → .env and fill in your secrets."
  exit 1
fi
set -a; source "$SCRIPT_DIR/.env"; set +a

# ── 1. Resource group ─────────────────────────────────────────────────────────
echo "▶ [1/6] Creating resource group '$RESOURCE_GROUP' in $LOCATION..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

# ── 2. Azure Container Registry (Basic – cheapest tier) ───────────────────────
echo "▶ [2/6] Creating Container Registry '$ACR_NAME' (Basic)..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true \
  --output none

ACR_SERVER="${ACR_NAME}.azurecr.io"
ACR_PASS="$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)"

# ── 3. Build for linux/amd64 and push to ACR ─────────────────────────────────
# Local images are arm64 (Apple Silicon); ACI requires amd64 Linux images.
echo "▶ [3/6] Building linux/amd64 images and pushing to $ACR_SERVER..."
echo "$ACR_PASS" | docker login "$ACR_SERVER" --username "$ACR_NAME" --password-stdin

docker buildx build \
  --platform linux/amd64 \
  --file "$SCRIPT_DIR/Dockerfile" \
  --tag "$ACR_SERVER/chromadbdemo-api:latest" \
  --build-arg SERVICE=api \
  --push \
  "$SCRIPT_DIR"

docker buildx build \
  --platform linux/amd64 \
  --file "$SCRIPT_DIR/Dockerfile" \
  --tag "$ACR_SERVER/chromadbdemo-streamlit:latest" \
  --push \
  "$SCRIPT_DIR"

# ── 4. Generate ACI multi-container YAML ─────────────────────────────────────
echo "▶ [4/6] Generating ACI deployment manifest..."
ACI_YAML="/tmp/aci-chromadb-deploy.yml"

cat > "$ACI_YAML" <<EOF
name: ${CONTAINER_GROUP}
apiVersion: '2021-10-01'
location: ${LOCATION}
properties:
  containers:

  - name: api
    properties:
      image: ${ACR_SERVER}/chromadbdemo-api:latest
      command: ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
      resources:
        requests:
          cpu: 0.5
          memoryInGB: 1.0
      ports:
      - port: 8000
      environmentVariables:
      - name: OPENAI_API_KEY
        secureValue: "${OPENAI_API_KEY}"
      - name: CHROMA_API_KEY
        secureValue: "${CHROMA_API_KEY}"
      - name: CHROMA_TENANT
        secureValue: "${CHROMA_TENANT}"
      - name: CHROMA_DATABASE
        secureValue: "${CHROMA_DATABASE}"
      - name: CHROMA_COLLECTION
        value: "${CHROMA_COLLECTION:-edureka-session-demo}"
      - name: CHROMA_TOP_K
        value: "${CHROMA_TOP_K:-4}"

  - name: streamlit
    properties:
      image: ${ACR_SERVER}/chromadbdemo-streamlit:latest
      command:
        - streamlit
        - run
        - upload_document.py
        - --server.port=8501
        - --server.address=0.0.0.0
        - --server.headless=true
      resources:
        requests:
          cpu: 0.5
          memoryInGB: 1.0
      ports:
      - port: 8501
      environmentVariables:
      - name: OPENAI_API_KEY
        secureValue: "${OPENAI_API_KEY}"
      - name: CHROMA_API_KEY
        secureValue: "${CHROMA_API_KEY}"
      - name: CHROMA_TENANT
        secureValue: "${CHROMA_TENANT}"
      - name: CHROMA_DATABASE
        secureValue: "${CHROMA_DATABASE}"
      - name: CHROMA_COLLECTION
        value: "${CHROMA_COLLECTION:-edureka-session-demo}"
      - name: CHROMA_TOP_K
        value: "${CHROMA_TOP_K:-4}"

  osType: Linux
  restartPolicy: Always

  imageRegistryCredentials:
  - server: ${ACR_SERVER}
    username: ${ACR_NAME}
    password: "${ACR_PASS}"

  ipAddress:
    type: Public
    dnsNameLabel: ${DNS_LABEL}
    ports:
    - protocol: TCP
      port: 8000
    - protocol: TCP
      port: 8501
EOF

# ── 5. Deploy to ACI ──────────────────────────────────────────────────────────
echo "▶ [5/6] Deploying container group to Azure (this takes ~2 min)..."
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --file "$ACI_YAML" \
  --output none

# ── 6. Retrieve endpoints ─────────────────────────────────────────────────────
echo "▶ [6/6] Fetching endpoints..."
FQDN="$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CONTAINER_GROUP" \
  --query "ipAddress.fqdn" -o tsv)"

# ── Save state for teardown ───────────────────────────────────────────────────
cat > "$STATE_FILE" <<STATE
RESOURCE_GROUP=${RESOURCE_GROUP}
ACR_NAME=${ACR_NAME}
CONTAINER_GROUP=${CONTAINER_GROUP}
STATE

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           Deployment Complete!                           ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  FastAPI RAG API  →  http://${FQDN}:8000"
echo "║  API Swagger Docs →  http://${FQDN}:8000/docs"
echo "║  Streamlit UI     →  http://${FQDN}:8501"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Resource group   :  ${RESOURCE_GROUP}"
echo "║  Location         :  ${LOCATION}"
echo "║  Est. cost        :  ~\$0.07/hr while running"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  To tear down:  bash teardown-azure.sh                  ║"
echo "╚══════════════════════════════════════════════════════════╝"

rm -f "$ACI_YAML"
