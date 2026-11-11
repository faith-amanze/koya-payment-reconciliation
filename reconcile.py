
#!/usr/bin/env python3

import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

payments = {}

# Read payment records and retain the latest attempt.
with open("payments.jsonl", "r", encoding="utf-8") as file:
    for line in file:
        try:
            event = json.loads(line)

            if not isinstance(event, dict):
                continue

            txn_id = event.get("txn_id")
            if not txn_id:
                continue

            timestamp = datetime.fromisoformat(
                event["ts"].replace("Z", "+00:00")
            )

            previous = payments.get(txn_id)

            if previous is None or timestamp >= previous["timestamp"]:
                payments[txn_id] = {
                    "timestamp": timestamp,
                    "status": event["status"],
                    "amount": event["amount"]
                }

        except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError):
            continue

# Keep only successful latest attempts.
successful = [
    payment for payment in payments.values()
    if payment["status"] == "success"
]

count = len(successful)
expected = int(Path("expected.txt").read_text().strip())

print(f"Successful payments: {count}")
print(f"Expected payments: {expected}")

if count != expected:
    print("Check failed: payment count mismatch.")
    raise SystemExit(1)

# Remove thousands separators before converting to Decimal.
total = sum(
    (
        Decimal(str(payment["amount"]).replace(",", ""))
        for payment in successful
    ),
    Decimal("0")
)

total = total.quantize(
    Decimal("1"),
    rounding=ROUND_HALF_UP
)

print("Check passed!")
print(f"Your code: KOYA-{total}")
