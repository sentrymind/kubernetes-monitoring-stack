# Kubernetes Monitoring Lab

A reproducible local observability lab for Kubernetes, built with Kind, Prometheus, Grafana, and the OpenTelemetry Collector.

This repository is intended for development, demonstrations, and configuration experiments. It is **not a production deployment**.

## What it installs

- a three-node Kind cluster;
- `kube-prometheus-stack` with Prometheus, Alertmanager, Grafana, node-exporter, and kube-state-metrics;
- an OpenTelemetry Collector that accepts OTLP metrics and traces;
- the OpenTelemetry Operator.

Metrics are exposed to Prometheus. Traces are written to the Collector's debug exporter so the ingestion path can be inspected without a separate trace backend.

## Repository layout

```text
.
├── kind-config.yaml
├── otel-collector-values.yaml
├── prometheus-values.yaml
└── setup.sh
```

## Requirements

- Docker
- Kind
- kubectl
- Helm 3

The setup script checks that Kind, kubectl, and Helm are available before changing the cluster.

## Quick start

```bash
git clone https://github.com/sentrymind/kubernetes-monitoring-stack.git
cd kubernetes-monitoring-stack
chmod +x setup.sh
./setup.sh
```

The script creates `monitoring-cluster`, installs the Helm releases, waits for their pods, and prints the local access details.

## Local endpoints

| Component | Endpoint |
|---|---|
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| OTLP gRPC | localhost:4317 |
| OTLP HTTP | localhost:4318 |

Grafana uses the chart-generated admin password. Retrieve it with:

```bash
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode
echo
```

## Useful commands

```bash
kubectl get pods -A
kubectl get pods -n monitoring
kubectl get pods -n otel-system
kubectl logs -n otel-system deployment/opentelemetry-collector
```

Delete the local cluster with:

```bash
kind delete cluster --name monitoring-cluster
```

## Configuration

- `kind-config.yaml` defines the local cluster and host-port mappings.
- `prometheus-values.yaml` configures Prometheus, Alertmanager, Grafana, and two Grafana dashboards.
- `otel-collector-values.yaml` configures OTLP receivers, metric export, resource limits, and debug trace output.
- `setup.sh` performs prerequisite checks and installs the Helm releases.

## Automated validation

The GitHub Actions workflow performs:

- ShellCheck on `setup.sh`;
- YAML linting;
- `helm template` rendering for the Prometheus and OpenTelemetry Collector configurations.

The workflow validates configuration syntax and chart rendering. It does not run a full end-to-end Kind installation.

## Limitations

- Local development only: no TLS, ingress policy, external authentication, high availability, or production hardening.
- Prometheus data is not configured for durable production storage.
- No Loki or other log backend is installed.
- No Tempo or other trace store is installed; traces go to the Collector debug exporter.
- Helm chart versions are not pinned, so upstream changes can affect future runs.
- Running `setup.sh` when `monitoring-cluster` already exists will fail at cluster creation.

## License

MIT — see [LICENSE](LICENSE).

## Issues

Report reproducible problems in the [issue tracker](https://github.com/sentrymind/kubernetes-monitoring-stack/issues).
