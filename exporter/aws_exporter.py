import boto3
import logging
from datetime import datetime, timedelta
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

def get_date_range():
    today = datetime.utcnow()
    start = today.replace(day=1).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    if start == end:
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return start, end

def get_yesterday_range():
    yesterday = datetime.utcnow() - timedelta(days=1)
    start = yesterday.strftime("%Y-%m-%d")
    end = datetime.utcnow().strftime("%Y-%m-%d")
    return start, end

def fetch_aws_costs():
    client = boto3.client("ce")
    start_month, end_today = get_date_range()
    start_yesterday, end_today2 = get_yesterday_range()

    result = {
        "monthly_total": 0.0,
        "daily_total": 0.0,
        "by_service": [],
        "error": None,
    }

    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_month, "End": end_today},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        service_monthly = {}
        for group in response["ResultsByTime"][0]["Groups"]:
            service = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            service_monthly[service] = cost

        result["monthly_total"] = sum(service_monthly.values())

        daily_response = client.get_cost_and_usage(
            TimePeriod={"Start": start_yesterday, "End": end_today2},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        service_daily = {}
        if daily_response["ResultsByTime"]:
            for group in daily_response["ResultsByTime"][0]["Groups"]:
                service = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                service_daily[service] = cost

        result["daily_total"] = sum(service_daily.values())

        all_services = set(service_monthly.keys()) | set(service_daily.keys())
        for svc in all_services:
            result["by_service"].append({
                "service": svc,
                "monthly_cost": service_monthly.get(svc, 0.0),
                "daily_cost": service_daily.get(svc, 0.0),
            })

        logger.info(f"[AWS] monthly=${result['monthly_total']:.4f}, daily=${result['daily_total']:.4f}")

    except ClientError as e:
        result["error"] = e.response["Error"]["Message"]
        logger.error(f"[AWS] ClientError: {result['error']}")
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"[AWS] Error: {e}")

    return result
