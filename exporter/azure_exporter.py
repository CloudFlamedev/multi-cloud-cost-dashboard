import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

AZURE_SERVICES = [
    {"service": "Virtual Machines",         "monthly_range": (0.0, 0.80), "daily_range": (0.0, 0.03)},
    {"service": "Azure Blob Storage",       "monthly_range": (0.0, 0.10), "daily_range": (0.0, 0.004)},
    {"service": "Azure Functions",          "monthly_range": (0.0, 0.05), "daily_range": (0.0, 0.002)},
    {"service": "Azure SQL Database",       "monthly_range": (0.0, 0.50), "daily_range": (0.0, 0.02)},
    {"service": "Azure App Service",        "monthly_range": (0.0, 0.20), "daily_range": (0.0, 0.008)},
    {"service": "Azure Cosmos DB",          "monthly_range": (0.0, 0.15), "daily_range": (0.0, 0.006)},
    {"service": "Azure Monitor",            "monthly_range": (0.0, 0.05), "daily_range": (0.0, 0.002)},
    {"service": "Azure Kubernetes Service", "monthly_range": (0.0, 0.30), "daily_range": (0.0, 0.01)},
]

_seed = int(datetime.utcnow().strftime("%Y%m%d"))

def fetch_azure_costs():
    random.seed(_seed)

    result = {
        "monthly_total": 0.0,
        "daily_total": 0.0,
        "by_service": [],
        "simulated": True,
        "error": None,
    }

    for svc in AZURE_SERVICES:
        monthly = round(random.uniform(*svc["monthly_range"]), 4)
        daily   = round(random.uniform(*svc["daily_range"]), 4)
        daily   = min(daily, monthly)

        result["by_service"].append({
            "service": svc["service"],
            "monthly_cost": monthly,
            "daily_cost": daily,
        })

    result["monthly_total"] = round(sum(s["monthly_cost"] for s in result["by_service"]), 4)
    result["daily_total"]   = round(sum(s["daily_cost"]   for s in result["by_service"]), 4)

    logger.info(f"[Azure][SIMULATED] monthly=${result['monthly_total']:.4f}, daily=${result['daily_total']:.4f}")

    return result
