import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402
from trade_republic.utils.tr_utils import TRUtils  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    portfolio_service = tr_client.portfolio_service
    account_service = tr_client.account_service

    # 1. Fetch portfolio by account type
    print("=" * 50)
    print("1. Fetching portfolio by account type...")
    accounts = await account_service.fetch_accounts()
    if accounts:
        for account in accounts:
            securities_account_number = account.get("securitiesAccountNumber")
            if securities_account_number:
                print(f"\n  Account: {securities_account_number} ({account.get('productType')})")
                portfolio_by_type = await portfolio_service.fetch_portfolio_by_type(securities_account_number)
                print(f"  Portfolio data keys: {list(portfolio_by_type.keys()) if portfolio_by_type else 'None'}")
                if portfolio_by_type:
                    categories = portfolio_by_type.get("categories", [])
                    print(f"  Number of categories: {len(categories)}")
                    for category in categories:
                        positions = category.get("positions", [])
                        print(f"    - Category: {category.get('categoryType')}, Positions: {len(positions)}")

    # 2. Fetch full portfolio (with detailed information)
    # Warning: This can take a long time as it fetches all instrument details
    print("\n" + "=" * 50)
    print("2. Fetching full portfolio with details...")
    print("(This may take a while as it fetches detailed information for all instruments)")
    portfolio = await portfolio_service.fetch_portfolio(tr_client)
    print(f"Number of accounts in portfolio: {len(portfolio)}")
    TRUtils.save_json(portfolio, os.path.join(tr_client.output_folder, "portfolio.json"))

    # 3. Fetch portfolio positions (flattened view)
    print("\n" + "=" * 50)
    print("3. Fetching portfolio positions (flattened view)...")

    # Without French classification
    print("\n  3a. Standard positions...")
    positions = await portfolio_service.fetch_portfolio_positions(tr_client, french_classification=False, add_cash=True)
    print(f"  Total positions (including cash): {len(positions)}")
    for position in positions[:3]:  # Show first 3 positions as example
        print(f"    - {position.get('name')} ({position.get('isin')})")
        print(f"      Size: {position.get('netSize')}, Current value: {position.get('current_valuation')}")
    TRUtils.save_json(positions, os.path.join(tr_client.output_folder, "portfolio_positions.json"))

    # With French classification (CTO/PEA labels)
    print("\n  3b. Positions with French classification (CTO/PEA)...")
    positions_french = await portfolio_service.fetch_portfolio_positions(
        tr_client, french_classification=True, add_cash=True
    )
    print(f"  Total positions: {len(positions_french)}")
    for position in positions_french[:3]:  # Show first 3 positions as example
        account_label = position.get("account_label", "N/A")
        print(f"    - [{account_label}] {position.get('name')} ({position.get('ticker')})")
    TRUtils.save_json(positions_french, os.path.join(tr_client.output_folder, "portfolio_positions_french.json"))

    # 4. Fetch portfolio status
    print("\n" + "=" * 50)
    print("4. Fetching portfolio status...")
    portfolio_status = await portfolio_service.fetch_portfolio_status()
    print(f"Portfolio status: {portfolio_status}")
    TRUtils.save_json(portfolio_status, os.path.join(tr_client.output_folder, "portfolio_status.json"))

    # 5. Fetch portfolio history for different timeframes
    print("\n" + "=" * 50)
    print("5. Fetching portfolio history...")
    timeframes = ["1w", "1m", "3m", "6m", "1y"]
    for timeframe in timeframes:
        print(f"\n  Timeframe: {timeframe}")
        portfolio_history = await portfolio_service.fetch_portfolio_history(timeframe)
        print(f"  History data keys: {list(portfolio_history.keys()) if portfolio_history else 'None'}")
        TRUtils.save_json(
            portfolio_history, os.path.join(tr_client.output_folder, f"portfolio_history_{timeframe}.json")
        )

    # 6. Fetch performance for a specific instrument
    print("\n" + "=" * 50)
    print("6. Fetching instrument performance...")
    # Bitcoin ISIN as example, replace with actual ISIN from your portfolio
    isin_example = "XF000BTC0017"
    exchange_example = "BHS"
    print(f"  Instrument: {isin_example} on {exchange_example}")
    portfolio_performance = await portfolio_service.fetch_performance(isin_example, exchange_example)
    print(f"  Performance data keys: {list(portfolio_performance.keys()) if portfolio_performance else 'None'}")
    TRUtils.save_json(
        portfolio_performance, os.path.join(tr_client.output_folder, f"portfolio_performance_{isin_example}.json")
    )

    print("\n" + "=" * 50)
    print("Portfolio examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
