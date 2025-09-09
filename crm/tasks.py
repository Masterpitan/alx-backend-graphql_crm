import datetime
import requests
from celery import shared_task
from datetime import datetime

@shared_task
def generate_crm_report():
    log_file = "/tmp/crm_report_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )
        data = response.json().get("data", {})

        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue"

    except Exception as e:
        message = f"{timestamp} - Error generating report: {str(e)}"

    with open(log_file, "a") as f:
        f.write(message + "\n")

    return message
