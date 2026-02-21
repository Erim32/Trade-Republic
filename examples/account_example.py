import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    account_service = tr_client.account_service

    # 1. Fetch accounts list
    print("=" * 50)
    print("1. Fetching accounts list...")
    accounts_list: list = await account_service.fetch_accounts()
    print(f"Found {len(accounts_list)} account(s):")
    for account in accounts_list:
        print(f"  - Securities Account: {account.get('securitiesAccountNumber')}")
        print(f"    Cash Account: {account.get('cashAccountNumber')}")
        print(f"    Product Type: {account.get('productType')}")
        print(f"    Currency: {account.get('currency')}")

    # 2. Fetch available cash
    print("\n" + "=" * 50)
    print("2. Fetching available cash...")
    (
        available_cash,
        amount,
        device_currency,
    ) = await account_service.fetch_available_cash()
    print(f"Available cash: {amount} {device_currency}")

    # 3. Fetch cash info
    print("\n" + "=" * 50)
    print("3. Fetching cash info...")
    cash_info = await account_service.fetch_cash()
    print(f"Cash info: {cash_info}")

    # 4. Fetch available cash for payout
    print("\n" + "=" * 50)
    print("4. Fetching available cash for payout...")
    cash_for_payout = await account_service.fetch_available_cash_for_payout()
    print(f"Cash available for payout: {cash_for_payout}")

    # 5. Fetch portfolio by account (for each securities account)
    if accounts_list:
        for account in accounts_list:
            securities_account_number = account.get("securitiesAccountNumber")
            if securities_account_number:
                print("\n" + "=" * 50)
                print(f"5. Fetching portfolio for account {securities_account_number}...")
                portfolio = await account_service.fetch_portfolio_by_account(securities_account_number)
                print(f"Portfolio data retrieved (keys: {list(portfolio.keys()) if portfolio else 'None'})")

    # 6. Fetch accounts with full details (advanced method)
    # Warning: This method fetches detailed information for all instruments
    # and can take a long time to execute
    print("\n" + "=" * 50)
    print("6. Fetching detailed accounts information (this may take a while)...")
    print("Uncomment the following lines to execute:")
    print("# detailed_accounts = await account_service.fetch_accounts_details(tr_client, accounts_list)")
    print("# print(f'Detailed accounts retrieved with portfolio valuations')")

    # Uncomment to use:
    # detailed_accounts = await account_service.fetch_accounts_details(tr_client, accounts_list)
    # for account in detailed_accounts:
    #     print(f"\nAccount: {account.get('securitiesAccountNumber')}")
    #     cash_available = account.get('cash_available', {})
    #     print(f"  Cash available: {cash_available.get('amount')} {cash_available.get('currencyId')}")
    #     portfolio = account.get('portfolio', {})
    #     if portfolio:
    #         categories = portfolio.get('categories', [])
    #         for category in categories:
    #             print(f"  Category: {category.get('categoryType')}")
    #             positions = category.get('positions', [])
    #             for position in positions:
    #                 print(f"    - {position.get('isin')}: {position.get('netSize')} units")
    #                 print(f"      Current price: {position.get('current_price')}")
    #                 print(f"      Current valuation: {position.get('current_valuation')}")

    print("\n" + "=" * 50)
    print("Account examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
