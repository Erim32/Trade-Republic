import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    order_service = tr_client.order_service
    market_data_service = tr_client.market_data_service

    # Example parameters
    isin = "XF000BTC0017"  # Bitcoin
    exchange = "BHS"
    order_type = "buy"
    size = 0.001
    expiry = "gfd"  # good for day

    # 1. Fetch current orders
    print("=" * 50)
    print("1. Fetching current orders...")
    print("-" * 50)
    orders = await order_service.fetch_orders()
    current_orders = orders.get("orders", [])
    print(f"Current orders: {len(current_orders)}")

    if current_orders:
        print("\nFirst 3 orders:")
        for i, order in enumerate(current_orders[:3], 1):
            print(f"  {i}. Order ID: {order.get('id', 'N/A')}")
            print(f"     ISIN: {order.get('isin', 'N/A')}")
            print(f"     Type: {order.get('type', 'N/A')}")
            print(f"     Status: {order.get('status', 'N/A')}")
            print(f"     Size: {order.get('size', 'N/A')}")

    # 2. Get current market price
    print("\n" + "=" * 50)
    print("2. Fetching current market price...")
    print("-" * 50)
    market_price_response: dict | None = await market_data_service.fetch_ticker(isin, exchange)
    if market_price_response is None:
        print("Failed to fetch market price.")
        return

    if order_type == "buy":
        market_price = float(market_price_response.get("ask", {}).get("price", 0))
    else:
        market_price = float(market_price_response.get("bid", {}).get("price", 0))

    print(f"Current market price for {isin} on {exchange}: {market_price} EUR")

    # 3. Create a limit order (COMMENTED - requires confirmation)
    print("\n" + "=" * 50)
    print("3. Creating a limit order...")
    print("-" * 50)

    limit_price = market_price
    cost = size * limit_price

    print("Proposed limit order:")
    print(f"  - Type: {order_type}")
    print(f"  - ISIN: {isin}")
    print(f"  - Size: {size} shares")
    print(f"  - Limit price: {limit_price} EUR")
    print(f"  - Estimated cost: {cost:.2f} + 1 EUR transaction fee")
    print(f"  - Expiry: {expiry}")

    if order_type == "buy" and market_price and limit_price >= market_price:
        print("⚠️  The limit price is above or equal to the current market price.")
        print("   The order may execute immediately.")
    elif order_type == "sell" and market_price and limit_price <= market_price:
        print("⚠️  The limit price is below or equal to the current market price.")
        print("   The order may execute immediately.")

    print("\nTo execute this order, uncomment the code below:")
    print("# confirm = input('[LIMIT] Proceed with this order? (yes/no): ')")
    print("# if confirm.lower() == 'yes':")
    print("#     order_limit = await order_service.create_limit_order(")
    print(f"#         isin='{isin}', exchange='{exchange}', order_type='{order_type}',")
    print(f"#         size={size}, limit={limit_price}, expiry='{expiry}',")
    print("#         expiry_date=None, warnings_shown=[])")
    print("#     print(f'Limit order response: {order_limit}')")

    # 4. Create a market order (COMMENTED - requires confirmation)
    print("\n" + "=" * 50)
    print("4. Creating a market order...")
    print("-" * 50)

    sell_fractions = False
    estimated_cost = size * market_price

    print("Proposed market order:")
    print(f"  - Type: {order_type}")
    print(f"  - ISIN: {isin}")
    print(f"  - Size: {size} shares")
    print(f"  - Market price: {market_price} EUR")
    print(f"  - Estimated cost: {estimated_cost:.2f} + 1 EUR transaction fee")
    print(f"  - Sell fractions: {sell_fractions}")
    print(f"  - Expiry: {expiry}")

    print("\nTo execute this order, uncomment the code below:")
    print("# confirm_market = input('[MARKET] Proceed with market order? (yes/no): ')")
    print("# if confirm_market.lower() == 'yes':")
    print("#     order_market = await order_service.create_market_order(")
    print(f"#         isin='{isin}', exchange='{exchange}', order_type='{order_type}',")
    print(f"#         size={size}, expiry='{expiry}', sell_fractions={sell_fractions},")
    print("#         expiry_date=None, warnings_shown=[])")
    print("#     print(f'Market order response: {order_market}')")
    print("#     TRUtils.save_json(order_market, os.path.join(tr_client.output_folder, 'market_order_response.json'))")

    # 5. Create a stop-market order (COMMENTED - requires confirmation)
    print("\n" + "=" * 50)
    print("5. Creating a stop-market order...")
    print("-" * 50)

    stop_price = market_price * 0.95  # Stop at 5% below current price (for sell) or above (for buy)

    print("Proposed stop-market order:")
    print(f"  - Type: {order_type}")
    print(f"  - ISIN: {isin}")
    print(f"  - Size: {size} shares")
    print(f"  - Stop price: {stop_price:.2f} EUR")
    print(f"  - Current market price: {market_price} EUR")
    print(f"  - Expiry: {expiry}")

    print("\nNote: A stop-market order will execute at market price once the stop price is reached.")
    print("To execute this order, uncomment the code below:")
    print("# confirm_stop = input('[STOP-MARKET] Proceed with stop-market order? (yes/no): ')")
    print("# if confirm_stop.lower() == 'yes':")
    print("#     order_stop = await order_service.create_stop_market_order(")
    print(f"#         isin='{isin}', exchange='{exchange}', order_type='{order_type}',")
    print(f"#         size={size}, stop={stop_price:.2f}, expiry='{expiry}',")
    print("#         expiry_date=None, warnings_shown=[])")
    print("#     print(f'Stop-market order response: {order_stop}')")

    # 6. Cancel an order (COMMENTED - requires order ID)
    print("\n" + "=" * 50)
    print("6. Canceling an order...")
    print("-" * 50)

    if current_orders:
        first_order_id = current_orders[0].get("id", "N/A")
        first_order_status = current_orders[0].get("status", "N/A")
        print(f"Example order ID from current orders: {first_order_id}")
        print(f"Status: {first_order_status}")

        if first_order_status in ["active", "pending", "open"]:
            print("\nTo cancel this order, uncomment the code below:")
            print(f"# confirm_cancel = input('Cancel order {first_order_id}? (yes/no): ')")
            print("# if confirm_cancel.lower() == 'yes':")
            print(f"#     cancel_response = await order_service.cancel_order('{first_order_id}')")
            print("#     print(f'Cancel response: {cancel_response}')")
        else:
            print(f"\nNote: Order status is '{first_order_status}', may not be cancelable.")
    else:
        print("No current orders to cancel.")
        print("To cancel an order, use:")
        print("# order_id = 'your-order-id-here'")
        print("# cancel_response = await order_service.cancel_order(order_id)")
        print("# print(f'Cancel response: {cancel_response}')")

    # 7. Fetch savings plans
    print("\n" + "=" * 50)
    print("7. Fetching savings plans...")
    print("-" * 50)

    savings_plans_response = await order_service.fetch_savings_plans()
    savings_plans = savings_plans_response.get("savingsPlans", [])
    print(f"Current savings plans: {len(savings_plans)}")

    if savings_plans:
        print("\nSavings plans details:")
        for i, plan in enumerate(savings_plans, 1):
            print(f"  {i}. Plan ID: {plan.get('id', 'N/A')}")
            print(f"     ISIN: {plan.get('isin', 'N/A')}")
            print(f"     Amount: {plan.get('amount', 'N/A')} EUR")
            print(f"     Interval: {plan.get('interval', 'N/A')}")
            print(f"     Status: {plan.get('status', 'N/A')}")
            print(f"     Next execution: {plan.get('nextExecutionDate', 'N/A')}")
    else:
        print("No active savings plans found.")

    # 8. Create a savings plan (COMMENTED - requires confirmation)
    print("\n" + "=" * 50)
    print("8. Creating a savings plan...")
    print("-" * 50)

    savings_amount = 2.0  # EUR
    savings_interval = "monthly"  # 'weekly', 'monthly', 'quarterly', 'yearly'
    savings_start_date = "2026-03-01"

    print("Proposed savings plan:")
    print(f"  - ISIN: {isin}")
    print(f"  - Amount: {savings_amount} EUR")
    print(f"  - Interval: {savings_interval}")
    print(f"  - Start date: {savings_start_date}")

    print("\nTo create this savings plan, uncomment the code below:")
    print("# confirm_savings = input('[SAVINGS PLAN] Create savings plan? (yes/no): ')")
    print("# if confirm_savings.lower() == 'yes':")
    print("#     savings_plan_response = await order_service.create_savings_plan(")
    print(f"#         isin='{isin}',")
    print(f"#         amount={savings_amount},")
    print(f"#         interval='{savings_interval}',")
    print(f"#         start_date='{savings_start_date}',")
    print("#         start_date_type='date',")
    print(f"#         start_date_value='{savings_start_date}',")
    print("#         warnings_shown=[])")
    print("#     print(f'Savings plan created: {savings_plan_response}')")

    # 9. Change a savings plan (COMMENTED - requires savings plan ID)
    print("\n" + "=" * 50)
    print("9. Changing a savings plan...")
    print("-" * 50)

    if savings_plans:
        first_plan_id = savings_plans[0].get("id", "N/A")
        current_amount = savings_plans[0].get("amount", 0)
        new_amount = current_amount + 10.0

        print(f"Example savings plan ID: {first_plan_id}")
        print(f"Current amount: {current_amount} EUR")
        print(f"New amount: {new_amount} EUR")

        print("\nTo modify this savings plan, uncomment the code below:")
        print(f"# confirm_change = input('Change savings plan {first_plan_id}? (yes/no): ')")
        print("# if confirm_change.lower() == 'yes':")
        print("#     change_response = await order_service.change_savings_plan(")
        print(f"#         savings_plan_id='{first_plan_id}',")
        print(f"#         isin='{isin}',")
        print(f"#         amount={new_amount},")
        print(f"#         interval='{savings_interval}',")
        print(f"#         start_date='{savings_start_date}',")
        print("#         start_date_type='date',")
        print(f"#         start_date_value='{savings_start_date}',")
        print("#         warnings_shown=[])")
        print("#     print(f'Savings plan changed: {change_response}')")
    else:
        print("No savings plans to modify.")
        print("To modify a savings plan, use:")
        print("# savings_plan_id = 'your-plan-id-here'")
        print("# change_response = await order_service.change_savings_plan(...)")

    # 10. Cancel a savings plan (COMMENTED - requires savings plan ID)
    print("\n" + "=" * 50)
    print("10. Canceling a savings plan...")
    print("-" * 50)

    if savings_plans:
        first_plan_id = savings_plans[0].get("id", "N/A")
        plan_status = savings_plans[0].get("status", "N/A")

        print(f"Example savings plan ID: {first_plan_id}")
        print(f"Status: {plan_status}")

        print("\nTo cancel this savings plan, uncomment the code below:")
        print(f"# confirm_cancel_plan = input('Cancel savings plan {first_plan_id}? (yes/no): ')")
        print("# if confirm_cancel_plan.lower() == 'yes':")
        print(f"#     cancel_plan_response = await order_service.cancel_savings_plan('{first_plan_id}')")
        print("#     print(f'Savings plan canceled: {cancel_plan_response}')")
    else:
        print("No savings plans to cancel.")
        print("To cancel a savings plan, use:")
        print("# savings_plan_id = 'your-plan-id-here'")
        print("# cancel_plan_response = await order_service.cancel_savings_plan(savings_plan_id)")

    print("\n" + "=" * 50)
    print("Order examples completed!")
    print("\n⚠️  NOTE: All order creation/modification/cancellation methods are COMMENTED")
    print("   to prevent accidental execution. Uncomment carefully before use.")


if __name__ == "__main__":
    asyncio.run(main())
