import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    transaction_service = tr_client.transaction_service

    # 1. Fetch all transactions (without details)
    print("=" * 50)
    print("1. Fetching all transactions (basic)...")
    print("-" * 50)
    await transaction_service.fetch_transactions(extract_details=False)
    print("Transactions fetched successfully (check output folder)")

    # 2. Fetch all transactions with details (slower but more complete)
    print("\n" + "=" * 50)
    print("2. Fetching all transactions with details...")
    print("-" * 50)
    await transaction_service.fetch_transactions(extract_details=True)
    print("Transactions with details fetched successfully")

    # 3. Fetch timeline (paginated)
    print("\n" + "=" * 50)
    print("3. Fetching timeline...")
    print("-" * 50)

    print("\n  3a. First page of timeline:")
    timeline = await transaction_service.fetch_timeline()
    items = timeline.get("items", [])
    print(f"  Timeline items: {len(items)}")

    # Show first few timeline items
    if items:
        print("\n  First 3 timeline items:")
        for i, item in enumerate(items[:3], 1):
            print(f"    {i}. Type: {item.get('eventType', 'N/A')}")
            print(f"       ID: {item.get('id', 'N/A')}")
            print(f"       Title: {item.get('title', 'N/A')}")
            print(
                f"       Amount: {item.get('amount', {}).get('value', 'N/A')} {item.get('amount', {}).get('currency', '')}"
            )

    # 3b. Pagination example
    print("\n  3b. Fetching next page of timeline:")
    after_cursor = timeline.get("cursors", {}).get("after")
    if after_cursor:
        timeline_page2 = await transaction_service.fetch_timeline(after=after_cursor)
        items_page2 = timeline_page2.get("items", [])
        print(f"  Page 2 items: {len(items_page2)}")
    else:
        print("  No more pages available")

    # 4. Fetch a specific transaction by ID
    print("\n" + "=" * 50)
    print("4. Fetching specific transaction details...")
    print("-" * 50)

    if items:
        # Use the first transaction from timeline as example
        first_item = items[0]
        transaction_id = first_item.get("id")

        if transaction_id:
            print(f"\n  Fetching details for transaction: {transaction_id}")
            transaction = await transaction_service.fetch_transaction(transaction_id)
            if transaction:
                print("  Transaction details retrieved:")
                print(f"    - Event Type: {transaction.get('eventType', 'N/A')}")
                print(f"    - Status: {transaction.get('status', 'N/A')}")
                print(f"    - Title: {transaction.get('title', 'N/A')}")
                if transaction.get("sections"):
                    print(f"    - Sections: {len(transaction.get('sections', []))}")
        else:
            print("  No transaction ID available")
    else:
        print("  No transactions available to fetch details")

    # 5. Fetch timeline detail
    print("\n" + "=" * 50)
    print("5. Fetching timeline detail...")
    print("-" * 50)

    if items:
        # Find a timeline item with an appropriate event type
        timeline_item = None
        for item in items:
            if item.get("id"):
                timeline_item = item
                break

        if timeline_item:
            timeline_id = timeline_item.get("id")
            print(f"\n  Fetching timeline detail for: {timeline_id}")
            print(f"  Event Type: {timeline_item.get('eventType', 'N/A')}")

            timeline_detail = await transaction_service.fetch_timeline_detail(timeline_id)
            if timeline_detail:
                print("  Timeline detail retrieved:")
                print(f"    - Keys: {list(timeline_detail.keys())}")
                print(f"    - Title: {timeline_detail.get('title', 'N/A')}")
        else:
            print("  No timeline item available")
    else:
        print("  No timeline items available")

    # 6. Fetch timeline detail for an order
    print("\n" + "=" * 50)
    print("6. Fetching timeline detail for order...")
    print("-" * 50)

    # Look for an order-related event in timeline
    order_item = None
    if items:
        for item in items:
            event_type = item.get("eventType", "")
            if "ORDER" in event_type.upper() or "TRADE" in event_type.upper():
                order_item = item
                break

    if order_item:
        order_id = order_item.get("id")
        print(f"\n  Fetching order timeline detail for: {order_id}")
        print(f"  Event Type: {order_item.get('eventType', 'N/A')}")

        order_timeline = await transaction_service.fetch_timeline_detail_order(order_id)
        if order_timeline:
            print("  Order timeline detail retrieved:")
            print(f"    - Keys: {list(order_timeline.keys())}")
        else:
            print("  No order timeline data available")
    else:
        print("  No order-related items found in timeline")
        print("  To test this method, replace with an actual order ID:")
        print("  # ORDER_ID = 'your-order-id-here'")
        print("  # order_timeline = await transaction_service.fetch_timeline_detail_order(ORDER_ID)")

    # 7. Fetch timeline detail for a savings plan
    print("\n" + "=" * 50)
    print("7. Fetching timeline detail for savings plan...")
    print("-" * 50)

    # Look for a savings plan-related event in timeline
    savings_plan_item = None
    if items:
        for item in items:
            event_type = item.get("eventType", "")
            if "SAVING" in event_type.upper() or "PLAN" in event_type.upper():
                savings_plan_item = item
                break

    if savings_plan_item:
        savings_plan_id = savings_plan_item.get("id")
        print(f"\n  Fetching savings plan timeline detail for: {savings_plan_id}")
        print(f"  Event Type: {savings_plan_item.get('eventType', 'N/A')}")

        savings_plan_timeline = await transaction_service.fetch_timeline_detail_savings_plan(savings_plan_id)
        if savings_plan_timeline:
            print("  Savings plan timeline detail retrieved:")
            print(f"    - Keys: {list(savings_plan_timeline.keys())}")
        else:
            print("  No savings plan timeline data available")
    else:
        print("  No savings plan-related items found in timeline")
        print("  To test this method, replace with an actual savings plan ID:")
        print("  # SAVINGS_PLAN_ID = 'your-savings-plan-id-here'")
        print(
            "  # savings_plan_timeline = await transaction_service.fetch_timeline_detail_savings_plan(SAVINGS_PLAN_ID)"
        )

    print("\n" + "=" * 50)
    print("Transaction examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
