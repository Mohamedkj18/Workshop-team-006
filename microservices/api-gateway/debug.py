import logging
from logtail import LogtailHandler
import requests

def main():
    print("DEBUG > debug.py (in main):\t\t running the debug.py file...")
    logger = logging.getLogger("test-betterstack")
    logger.setLevel(logging.DEBUG)

    handler = LogtailHandler(source_token="UGi5GVckYGw9m5HnWo422J3w")
    logger.addHandler(handler)

    logger.error("✅ Test error from isolated script")
    debug_blocking()

def debug_blocking():
    response = requests.post(
        "https://in.logtail.com",
        headers={"Authorization": "Bearer UGi5GVckYGw9m5HnWo422J3w"},
        json={"message": "Test from requests", "level": "error"}
    )
    print("DEBUG > debug.py (in debug_blocking):\t",response.status_code)
    print("DEBUG > debug.py (in debug_blocking):\t",response.text)