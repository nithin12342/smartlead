# SmartLead - AI-Powered Lead Scoring System

## Project Overview

**Project Name:** SmartLead  
**Version:** 1.0.0  
**Organization:** Dulux Tech  
**Methodology:** Spec-Driven Development with Hardness Engineering

## Architecture

### Compute Platform
- **Platform:** Azure Kubernetes Service (AKS)
- **Kubernetes Version:** 1.28+
- **Node Pool:** Standard_D4s_v3 (4 vCPU, 16 GB RAM)
- **Min Nodes:** 2 | **Max Nodes:** 6

### API Layer
- **Framework:** FastAPI 0.104+
- **Server:** Uvicorn (ASGI) with Gunicorn workers
- **Workers:** 4 | **Timeout:** 120s
- **Endpoints:**
  - `/score-lead` - Single lead scoring
  - `/batch-score` - Batch lead scoring
  - `/health` - Health check
  - `/metrics` - Prometheus metrics

### Data Layer
- **Database:** Azure Database for PostgreSQL 14
- **Cache:** Azure Cache for Redis (Valkey) 7.0
- **Storage:** Azure Blob Storage with MinIO Gateway

### ML Platform
- **Tracking:** MLflow 2.11+
- **Feature Store:** Feast 0.35+
- **Orchestration:** Apache Airflow 2.8+
- **Training:** Kubeflow Pipelines

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn src.api.main:app --reload

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t smartlead-api:latest -f docker/Dockerfile.api .
```

## Project Structure

```
SmartLead/
├── src/
│   ├── api/              # FastAPI application
│   ├── ml/               # ML models and inference
│   ├── features/         # Feature engineering
│   └── utils/            # Utilities
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docker/               # Dockerfiles
├── k8s/                   # Kubernetes manifests
├── terraform/            # Infrastructure as Code
├── scripts/               # Automation scripts
└── pipelines/             # ML pipelines
```

## Success Criteria

| Metric | Target |
|--------|--------|
| API Availability | 99.9% |
| API Latency (p99) | <100ms |
| Model AUC | >0.85 |
| Feature Freshness | <5 minutes |
| Deployment Frequency | 10+/day |

## Security

- OAuth2/OIDC via Azure AD
- TLS 1.3 for all transit
- Azure Key Vault for secrets
- Network policies with Calico

## Monitoring

- Prometheus + Grafana
- OpenTelemetry tracing
- Loki for log aggregation
- Alerting via PagerDuty/Slack
