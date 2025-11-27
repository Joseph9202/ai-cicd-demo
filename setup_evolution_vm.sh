#!/bin/bash
# Setup script for Evolution API v2 on Google Cloud Compute Engine (e2-micro)
# Usage: ./setup_evolution_vm.sh

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE_NAME="evolution-api-server"
MACHINE_TYPE="e2-micro"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

echo "🚀 Iniciando setup de Evolution API en GCP ($INSTANCE_NAME)..."
echo "============================================================"

# 1. Create VM Instance
echo "📦 Creando instancia VM ($MACHINE_TYPE)..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --tags=http-server,https-server,evolution-api \
    --metadata=startup-script='#! /bin/bash
# Install Docker & Docker Compose
apt-get update
apt-get install -y docker.io docker-compose

# Create app directory
mkdir -p /opt/evolution-api
cd /opt/evolution-api

# Generate secure API Key
API_KEY=$(openssl rand -hex 16)
echo "AUTHENTICATION_API_KEY=$API_KEY" > .env

# Create docker-compose.yml
cat > docker-compose.yml <<EOF
version: "3.3"
services:
  evolution-api:
    image: atendai/evolution-api:v2.1.1
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=http://localhost:8080
      - AUTHENTICATION_API_KEY=\${AUTHENTICATION_API_KEY}
      - DATABASE_ENABLED=false
      - LOG_LEVEL=ERROR
      - DEL_INSTANCE=false
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store

volumes:
  evolution_instances:
  evolution_store:
EOF

# Start Evolution API
docker-compose up -d

# Save API Key to a file for retrieval
echo $API_KEY > /var/log/evolution_api_key.txt
'

if [ $? -eq 0 ]; then
    echo "✅ Instancia creada exitosamente."
else
    echo "❌ Error creando instancia."
    exit 1
fi

# 2. Create Firewall Rule
echo "🛡️ Configurando Firewall (puerto 8080)..."
gcloud compute firewall-rules create allow-evolution-api \
    --project=$PROJECT_ID \
    --allow tcp:8080 \
    --target-tags=evolution-api \
    --description="Allow Evolution API traffic" 2>/dev/null || echo "⚠️ Regla de firewall ya existe o error menor."

echo "⏳ Esperando a que la VM inicie y configure Docker (esto toma ~2-3 mins)..."
sleep 120

# 3. Retrieve IP and API Key
echo "🔍 Obteniendo datos de conexión..."
VM_IP=$(gcloud compute instances describe $INSTANCE_NAME --project=$PROJECT_ID --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "🔑 Intentando recuperar API Key de la VM..."
# We try to read the file created by startup script via SSH (might fail if not ready yet)
# Note: This requires SSH access enabled. If not, user might need to check serial port logs.
# For simplicity in this demo, we'll try to grep it from serial port output which is safer for automation.

API_KEY=$(gcloud compute instances get-serial-port-output $INSTANCE_NAME --project=$PROJECT_ID --zone=$ZONE | grep "AUTHENTICATION_API_KEY=" | tail -n 1 | cut -d'=' -f2 | tr -d '\r')

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETADO"
echo "════════════════════════════════════════════════════"
echo "🌍 Evolution API URL: http://$VM_IP:8080"
echo "🔑 API Key: $API_KEY"
echo ""
echo "⚠️ IMPORTANTE: Guarda estos datos. Los necesitarás para el bot."
echo "Si la API Key aparece vacía, espera 1 minuto más y corre:"
echo "gcloud compute instances get-serial-port-output $INSTANCE_NAME --zone=$ZONE | grep AUTHENTICATION_API_KEY"
echo "════════════════════════════════════════════════════"
