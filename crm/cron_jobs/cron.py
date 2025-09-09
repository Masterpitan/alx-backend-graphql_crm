import datetime
import requests

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Write heartbeat log
    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Optional: query GraphQL hello field to ensure endpoint is alive
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.ok:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello response: {response.json()}\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint not responding properly\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} Error reaching GraphQL: {e}\n")
