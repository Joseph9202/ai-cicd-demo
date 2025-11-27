#!/bin/bash
# Setup Cloud Storage bucket for PDF reports

PROJECT_ID="travel-recomender"
BUCKET_NAME="travel-recomender-garch-reports"
REGION="us-east1"

echo "🪣 Configurando Cloud Storage para PDFs"
echo "========================================"
echo ""

# Check if bucket exists
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✅ Bucket ya existe: gs://$BUCKET_NAME"
else
    echo "📦 Creando bucket..."
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ Bucket creado: gs://$BUCKET_NAME"
    else
        echo "❌ Error creando bucket"
        exit 1
    fi
fi

# Set bucket to publicly readable (for PDF access)
echo ""
echo "🔓 Configurando permisos públicos para PDFs..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

if [ $? -eq 0 ]; then
    echo "✅ Permisos configurados"
else
    echo "⚠️  Error configurando permisos (puede que ya estén configurados)"
fi

# Set lifecycle to delete old reports after 90 days
echo ""
echo "⏰ Configurando lifecycle (eliminar después de 90 días)..."

cat > /tmp/lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME

if [ $? -eq 0 ]; then
    echo "✅ Lifecycle configurado"
else
    echo "⚠️  Error configurando lifecycle"
fi

rm /tmp/lifecycle.json

echo ""
echo "═══════════════════════════════════════"
echo "✅ Cloud Storage Configurado"
echo "═══════════════════════════════════════"
echo ""
echo "Bucket URL: gs://$BUCKET_NAME"
echo "Public URL base: https://storage.googleapis.com/$BUCKET_NAME/"
echo ""
echo "Los PDFs se guardarán automáticamente en este bucket."
echo ""
