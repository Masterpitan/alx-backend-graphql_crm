#!/usr/bin/env python3
import sys
import os
import datetime
import asyncio
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# GraphQL query to get orders from the last 7 days
QUERY = gql("""
query GetRecentOrders($dateGte: Date!) {
  allOrders(orderDate_Gte: $dateGte) {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
""")

async def fetch_orders():
    # Calculate date from 7 days ago
    date_gte = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url=GRAPHQL_ENDPOINT,
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Execute query
    result = client.execute(QUERY, variable_values={"dateGte": date_gte})
    return result["allOrders"]["edges"]

def log_orders(orders):
    with open(LOG_FILE, "a") as f:
        for order in orders:
            order_id = order["node"]["id"]
            email = order["node"]["customer"]["email"]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Order {order_id}, Customer Email: {email}\n")

async def main():
    try:
        orders = await fetch_orders()
        log_orders(orders)
        print("Order reminders processed!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
