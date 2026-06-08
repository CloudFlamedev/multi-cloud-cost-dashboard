# 🌩️ Multi-Cloud Cost Dashboard

Real-time cloud cost monitoring dashboard for AWS (live) and Azure (simulated) built with Python, Prometheus, and Grafana.

## 🏗️ Architecture

AWS Cost Explorer → Python Exporter → Prometheus → Grafana
Azure (Simulated) → Python Exporter ↗

## 📦 Tech Stack
- **Python + boto3** — AWS Cost Explorer API
- **Prometheus** — Metrics storage
- **Grafana** — Dashboard & visualization

## 🚀 Quick Start
```bash
# Clone repo
git clone https://github.com/CloudFlamedev/multi-cloud-cost-dashboard

# Install dependencies
pip install -r exporter/requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your AWS keys

# Run exporter
cd exporter && python3 main.py
```

## 📊 Dashboard Panels
- AWS Monthly Spend
- Azure Monthly Spend  
- Total Cloud Spend
- Daily Cost Trend
- Azure Cost by Service
- AWS Cost by Service

## ⚠️ Note
Azure data is simulated for demo purposes.
