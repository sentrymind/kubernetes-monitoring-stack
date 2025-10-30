# 🚀 Kubernetes Monitoring Stack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.25+-blue.svg)](https://kubernetes.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Latest-orange.svg)](https://prometheus.io/)

**Production-ready Kubernetes observability stack in 5 minutes**

Complete monitoring solution with Prometheus, Grafana, and OpenTelemetry that actually works out of the box. The repository now ships with production-ready Kind, Prometheus, and OpenTelemetry configuration so the setup script works without any manual tweaks.

---

## 🎯 Why This Project?

Setting up Kubernetes monitoring shouldn't take days. Most tutorials give you broken configs and leave you debugging for hours.

**This gives you:**
- ✅ **Works immediately** - One command, everything configured
- ✅ **Production-ready** - Battle-tested configurations, not toy examples
- ✅ **Complete observability** - Metrics, traces, and logs in one stack
- ✅ **Beautiful dashboards** - Pre-configured Grafana dashboards
- ✅ **Best practices** - Security, performance, and reliability built-in

---

## 📦 What's Included

| Component | Purpose | Access |
|-----------|---------|--------|
| **Prometheus** | Metrics collection & storage | http://localhost:9090 |
| **Grafana** | Visualization & dashboards | http://localhost:3000 |
| **AlertManager** | Alert routing & management | Built-in |
| **OpenTelemetry Collector** | Traces & metrics ingestion | localhost:4317 (gRPC) |
| **OpenTelemetry Operator** | Auto-instrumentation | Built-in |
| **Node Exporter** | Node metrics | Built-in |
| **Kube State Metrics** | K8s cluster metrics | Built-in |

---

## ⚡ Quick Start

### Prerequisites

```bash
# Required
docker         # Container runtime
kind          # Kubernetes in Docker (v0.20.0+)
kubectl       # Kubernetes CLI
helm          # Package manager (v3.12.0+)

# Install on macOS
brew install kind kubectl helm

# Install on Linux - see docs
```

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/sentry/kubernetes-monitoring-stack.git
cd kubernetes-monitoring-stack

# Run the setup script (will validate all required files)
chmod +x setup.sh
./setup.sh

# That's it! 🎉
```

**Time:** ~5-7 minutes on a typical machine

---

## 🎨 Access Your Stack

### Grafana
```
URL:      http://localhost:3000
Username: admin
Password: (displayed in setup output)

# Or get password anytime:
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode
```

**Pre-loaded dashboards:**
- Kubernetes Cluster Overview
- Kubernetes Pods Monitoring
- OpenTelemetry Collector Metrics

### Prometheus
```
URL: http://localhost:9090

# Example queries:
rate(http_requests_total[5m])
up{job="kubernetes-nodes"}
```

### OpenTelemetry Collector
```
OTLP gRPC: localhost:4317
OTLP HTTP: localhost:4318

> ℹ️ The Kind cluster exposes NodePorts for Grafana (30000) and Prometheus (30900) and the Kind configuration automatically maps them to localhost ports 3000 and 9090 respectively. The OTLP ports are also mapped so you can push telemetry data without any additional port-forwarding.

# Send test metrics:
docker run --network=host otel/telemetrygen:latest metrics \
  --otlp-endpoint localhost:4317 \
  --otlp-insecure \
  --duration 30s
```

---

## 🔧 Common Commands

```bash
# Check status of all components
kubectl get pods -A

# View Prometheus pods
kubectl get pods -n monitoring

# View OpenTelemetry pods
kubectl get pods -n otel-system

# Get Grafana password
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Delete cluster
kind delete cluster --name monitoring-cluster
```

---

## 📚 Documentation

- **Installation Guide** - Detailed setup instructions
- **Architecture Overview** - How components fit together
- **Configuration Guide** - Customization options
- **Troubleshooting** - Common issues and solutions
- **Best Practices** - Production recommendations

---

## 🎓 Examples

### Python Application with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my-operation"):
    # Your code here
    pass
```

More examples coming soon!

---

## 🛠️ Customization

### Change Prometheus Retention

Edit `prometheus-values.yaml`:
```yaml
prometheus:
  prometheusSpec:
    retention: 30d  # Default: 7d
```

### Add Custom Dashboards

All of the Helm value files live at the repository root:

```text
kind-config.yaml            # Kind cluster topology and port mappings
prometheus-values.yaml      # kube-prometheus-stack overrides
otel-collector-values.yaml  # OpenTelemetry Collector configuration
```

These files are validated by `setup.sh` before any Kubernetes resources are created. Feel free to fork the repo and adjust the defaults to match your infrastructure (e.g., different retention policies, Grafana datasources, or OTLP exporters).

Edit `prometheus-values.yaml`:
```yaml
grafana:
  dashboards:
    default:
      my-dashboard:
        gnetId: 12345
        revision: 1
        datasource: Prometheus
```

---

## 🐛 Troubleshooting

### Pods not starting?
```bash
kubectl get events -n monitoring --sort-by='.lastTimestamp'
kubectl describe pod -n monitoring <pod-name>
```

### Can't access Grafana?
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Out of disk space?
```bash
kind delete cluster --name monitoring-cluster
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with reproduction steps
2. **Suggest features** - Tell us what you need
3. **Submit PRs** - Fix bugs or add features
4. **Improve docs** - Help others understand better
5. **Share** - Star ⭐ the repo and tell others

---

## 🤖 AI Agents

This repository also includes specialized AI agents for various tasks:

### Scientific History Agent

An intelligent agent for searching and analyzing academic sources focused on 20th century history (1900-1999).

**Features:**
- Multi-source search (CrossRef, Semantic Scholar, CORE)
- Automatic temporal filtering (1900-1999)
- Contextual search with historical keywords
- Export to JSON, Markdown, CSV formats

**Quick Start:**

```bash
cd agents/scientific-history-agent
pip install -r requirements.txt
python scientific_history_agent.py "Первая мировая война" --output results.md
```

**Documentation:** See [agents/scientific-history-agent/README.md](agents/scientific-history-agent/README.md)

---

## 📈 Roadmap

- [ ] Support for Loki (log aggregation)
- [ ] Tempo integration (distributed tracing)
- [ ] Multi-cluster monitoring
- [ ] Cost analysis dashboard
- [ ] Helm chart distribution
- [ ] AWS/GCP/Azure guides
- [x] Scientific History Agent for 20th century research

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with amazing open-source projects:
- [Prometheus](https://prometheus.io/) - Metrics and monitoring
- [Grafana](https://grafana.com/) - Visualization
- [OpenTelemetry](https://opentelemetry.io/) - Observability framework
- [Kind](https://kind.sigs.k8s.io/) - Kubernetes in Docker
- [Helm](https://helm.sh/) - Package management

---

## 📞 Support

- 📖 Documentation (coming soon)
- 🐛 [Issue Tracker](https://github.com/sentry/kubernetes-monitoring-stack/issues)
- 💬 Discussions (coming soon)

---

<div align="center">

**Made with ❤️ for the Kubernetes community**

[⬆ Back to Top](#-kubernetes-monitoring-stack)

</div>
