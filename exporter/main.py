import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Info
from aws_exporter import fetch_aws_costs
from azure_exporter import fetch_azure_costs

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

EXPORTER_PORT   = int(os.getenv("EXPORTER_PORT", 8000))
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 3600))

# ── Prometheus Metrics ─────────────────────────────────────
monthly_total      = Gauge("cloud_cost_monthly_total",      "Total monthly spend USD",         ["provider"])
daily_total        = Gauge("cloud_cost_daily_total",        "Total daily spend USD",            ["provider"])
monthly_by_service = Gauge("cloud_cost_monthly_by_service", "Monthly spend per service USD",   ["provider", "service"])
daily_by_service   = Gauge("cloud_cost_daily_by_service",   "Daily spend per service USD",     ["provider", "service"])
scrape_success     = Gauge("cloud_exporter_last_scrape_success",   "1=success 0=error",        ["provider"])
scrape_timestamp   = Gauge("cloud_exporter_last_scrape_timestamp", "Unix timestamp last scrape",["provider"])
exporter_info      = Info("cloud_cost_exporter", "Exporter metadata")

def update_aws_metrics():
    logger.info("Fetching AWS costs...")
    data = fetch_aws_costs()
    if data["error"]:
        logger.error(f"[AWS] Failed: {data['error']}")
        scrape_success.labels(provider="aws").set(0)
        return
    monthly_total.labels(provider="aws").set(data["monthly_total"])
    daily_total.labels(provider="aws").set(data["daily_total"])
    for item in data["by_service"]:
        monthly_by_service.labels(provider="aws", service=item["service"]).set(item["monthly_cost"])
        daily_by_service.labels(provider="aws",   service=item["service"]).set(item["daily_cost"])
    scrape_success.labels(provider="aws").set(1)
    scrape_timestamp.labels(provider="aws").set(time.time())
    logger.info(f"[AWS] Done — monthly=${data['monthly_total']:.4f}")

def update_azure_metrics():
    logger.info("Fetching Azure costs (simulated)...")
    data = fetch_azure_costs()
    if data["error"]:
        scrape_success.labels(provider="azure").set(0)
        return
    monthly_total.labels(provider="azure").set(data["monthly_total"])
    daily_total.labels(provider="azure").set(data["daily_total"])
    for item in data["by_service"]:
        monthly_by_service.labels(provider="azure", service=item["service"]).set(item["monthly_cost"])
        daily_by_service.labels(provider="azure",   service=item["service"]).set(item["daily_cost"])
    scrape_success.labels(provider="azure").set(1)
    scrape_timestamp.labels(provider="azure").set(time.time())
    logger.info(f"[Azure] Done — monthly=${data['monthly_total']:.4f}")

def collect_all():
    update_aws_metrics()
    update_azure_metrics()

if __name__ == "__main__":
    exporter_info.info({
        "version": "1.0.0",
        "providers": "aws,azure",
        "azure_mode": "simulated",
        "started_at": datetime.utcnow().isoformat(),
    })
    logger.info(f"🚀 Starting exporter on port {EXPORTER_PORT}")
    logger.info(f"📊 Metrics at: http://localhost:{EXPORTER_PORT}/metrics")
    logger.info(f"⏱️  Scrape interval: {SCRAPE_INTERVAL}s")
    start_http_server(EXPORTER_PORT)
    collect_all()
    while True:
        time.sleep(SCRAPE_INTERVAL)
        collect_all()
