#!/bin/bash
# setup.sh - Automated infrastructure bootstrap script

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

required_files=(
  "${ROOT_DIR}/kind-config.yaml"
  "${ROOT_DIR}/prometheus-values.yaml"
  "${ROOT_DIR}/otel-collector-values.yaml"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "❌ Required configuration file not found: $file"
    echo "   Make sure you've cloned the entire repository or restored the file."
    exit 1
  fi
done

echo "🚀 Starting infrastructure bootstrap..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v kind >/dev/null 2>&1 || { echo "❌ kind is required but not installed. Install from https://kind.sigs.k8s.io/"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "❌ helm is required but not installed."; exit 1; }

# Create Kind cluster
echo -e "${GREEN}📦 Creating Kind cluster...${NC}"
kind create cluster --config "${ROOT_DIR}/kind-config.yaml"

# Wait for cluster to be ready
echo -e "${YELLOW}⏳ Waiting for cluster to be ready...${NC}"
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Create namespaces
echo -e "${GREEN}📁 Creating namespaces...${NC}"
kubectl create namespace monitoring || true
kubectl create namespace otel-system || true

# Add Helm repositories
echo -e "${GREEN}📚 Adding Helm repositories...${NC}"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

# Install Prometheus
echo -e "${GREEN}📊 Installing Prometheus...${NC}"
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values "${ROOT_DIR}/prometheus-values.yaml" \
  --wait

# Install OpenTelemetry Collector
echo -e "${GREEN}🔭 Installing OpenTelemetry Collector...${NC}"
helm upgrade --install opentelemetry-collector open-telemetry/opentelemetry-collector \
  --namespace otel-system \
  --values "${ROOT_DIR}/otel-collector-values.yaml" \
  --wait

# Install OpenTelemetry Operator
echo -e "${GREEN}🎯 Installing OpenTelemetry Operator...${NC}"
helm upgrade --install opentelemetry-operator open-telemetry/opentelemetry-operator \
  --namespace otel-system \
  --set manager.collectorImage.repository=otel/opentelemetry-collector-k8s \
  --wait

# Wait for all pods to be ready
echo -e "${YELLOW}⏳ Waiting for all pods to be ready...${NC}"
kubectl wait --for=condition=Ready pods --all -n monitoring --timeout=300s
kubectl wait --for=condition=Ready pods --all -n otel-system --timeout=300s

# Get access information
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Access Information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎨 Grafana:"
echo "   URL: http://localhost:3000"
echo "   Username: admin"
echo "   Password: $(kubectl get secret -n monitoring prometheus-grafana -o jsonpath='{.data.admin-password}' | base64 --decode)"
echo ""
echo "📈 Prometheus:"
echo "   URL: http://localhost:9090"
echo ""
echo "🔭 OpenTelemetry Collector:"
echo "   OTLP gRPC: localhost:4317"
echo "   OTLP HTTP: localhost:4318"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
