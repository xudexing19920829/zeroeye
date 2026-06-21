#!/usr/bin/env python3
"""
Health check for Prometheus stale metrics detection.

This script checks for stale metrics in Prometheus and alerts when
metrics haven't been updated within the expected timeframe.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class StaleMetricsChecker:
    """Check for stale Prometheus metrics."""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.stale_threshold_minutes = 5
        self.alert_webhook = os.getenv("ALERT_WEBHOOK_URL")
    
    def query_metric(self, metric_name: str) -> Optional[Dict]:
        """Query Prometheus for a metric."""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": metric_name},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success" and data["data"]["result"]:
                return data["data"]["result"][0]
            return None
        except Exception as e:
            print(f"Error querying {metric_name}: {e}")
            return None
    
    def check_metric_freshness(self, metric_name: str) -> Dict:
        """Check if a metric is fresh (updated recently)."""
        result = self.query_metric(metric_name)
        
        if not result:
            return {
                "metric": metric_name,
                "status": "missing",
                "message": "Metric not found",
                "stale": True
            }
        
        # Get the timestamp from the metric
        timestamp = result.get("value", [None, None])[0]
        if not timestamp:
            return {
                "metric": metric_name,
                "status": "error",
                "message": "No timestamp in metric",
                "stale": True
            }
        
        # Calculate age
        metric_time = datetime.fromtimestamp(float(timestamp))
        age = datetime.now() - metric_time
        stale = age > timedelta(minutes=self.stale_threshold_minutes)
        
        return {
            "metric": metric_name,
            "status": "stale" if stale else "fresh",
            "age_minutes": age.total_seconds() / 60,
            "last_updated": metric_time.isoformat(),
            "stale": stale
        }
    
    def check_all_metrics(self, metrics: List[str]) -> List[Dict]:
        """Check freshness of multiple metrics."""
        results = []
        for metric in metrics:
            result = self.check_metric_freshness(metric)
            results.append(result)
        return results
    
    def send_alert(self, stale_metrics: List[Dict]):
        """Send alert for stale metrics."""
        if not self.alert_webhook:
            print("No alert webhook configured")
            return
        
        message = {
            "text": "🚨 Stale Metrics Alert",
            "attachments": [{
                "color": "danger",
                "fields": [{
                    "title": "Stale Metrics",
                    "value": "\n".join([
                        f"- {m['metric']}: {m['age_minutes']:.1f} minutes old"
                        for m in stale_metrics
                    ]),
                    "short": False
                }]
            }]
        }
        
        try:
            response = requests.post(
                self.alert_webhook,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            print("Alert sent successfully")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def run_check(self, metrics: List[str]) -> Dict:
        """Run complete health check."""
        results = self.check_all_metrics(metrics)
        stale_metrics = [r for r in results if r["stale"]]
        
        if stale_metrics:
            self.send_alert(stale_metrics)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(results),
            "stale_metrics": len(stale_metrics),
            "fresh_metrics": len(results) - len(stale_metrics),
            "results": results
        }


def main():
    """Main function."""
    checker = StaleMetricsChecker()
    
    # Default metrics to check
    metrics = [
        "up",
        "http_requests_total",
        "http_request_duration_seconds",
        "process_cpu_seconds_total",
        "process_resident_memory_bytes"
    ]
    
    # Run check
    result = checker.run_check(metrics)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    # Exit with error if stale metrics found
    if result["stale_metrics"] > 0:
        print(f"\n⚠️  Found {result['stale_metrics']} stale metrics!")
        sys.exit(1)
    else:
        print(f"\n✅ All {result['total_metrics']} metrics are fresh!")
        sys.exit(0)


if __name__ == "__main__":
    main()
