import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# GraphQL endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Build GraphQL client
transport = RequestsHTTPTransport(
    url=GRAPHQL_ENDPOINT,
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Compute date range (last 7 days)
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# GraphQL query
query = gql("""
query GetRecentOrders($startDate: Date!) {
  allOrders(orderDate_Gte: $startDate) {
    id
    orderDate
    customer {
      email
    }
  }
}
""")

params = {"startDate": seven_days_ago.isoformat()}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("allOrders", [])

    for order in orders:
        order_id = order["id"]
        customer_email = order["customer"]["email"]
        log_entry = f"{datetime.datetime.now()} - Order {order_id} reminder sent to {customer_email}"
        logging.info(log_entry)

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"{datetime.datetime.now()} - Error processing reminders: {e}")
    print(f"Error: {e}")
