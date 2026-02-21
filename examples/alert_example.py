import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    alert_service = tr_client.alert_service

    # Fetch all existing price alarms
    print("1. Fetching all price alarms:")
    alarms = await alert_service.fetch_price_alarms()
    print(f"Total price alarms: {len(alarms.get('priceAlarms', []))}")
    print(alarms)
    print()

    # Create a new price alert
    print("2. Creating a new price alert:")
    ISIN = "XF000BTC0017"  # Bitcoin
    TARGET_PRICE = 49875.0
    create_response = await alert_service.create_price_alert(ISIN, TARGET_PRICE)
    print(f"Alert created for {ISIN} at {TARGET_PRICE} EUR")
    print(create_response)
    print()

    # Cancel a price alert (uncomment and replace with actual alarm ID)
    print("3. Cancelling a price alert:")
    ALARM_ID = "your-alarm-id-here"
    cancel_response = await alert_service.cancel_price_alert(ALARM_ID)
    print(f"Alert {ALARM_ID} cancelled")
    print(cancel_response)

    print("DONE")


if __name__ == "__main__":
    asyncio.run(main())
