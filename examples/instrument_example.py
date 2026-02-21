import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    instrument_service = tr_client.instrument_service

    # Example ISINs for testing
    bitcoin_isin = "XF000BTC0017"  # Bitcoin
    apple_isin = "US0378331005"  # Apple Inc.

    # 1. Fetch basic instrument information
    print("=" * 50)
    print("1. Fetching basic instrument information...")
    print("-" * 50)

    print(f"\n  1a. Fetching instrument info for Bitcoin ({bitcoin_isin}):")
    bitcoin_info = await instrument_service.fetch_instrument(bitcoin_isin)
    if bitcoin_info:
        print(f"  - Name: {bitcoin_info.get('shortName', 'N/A')}")
        print(f"  - Type: {bitcoin_info.get('typeId', 'N/A')}")
        print(f"  - ISIN: {bitcoin_info.get('isin', 'N/A')}")
        print(f"  - Exchange IDs: {bitcoin_info.get('exchangeIds', [])}")

    print(f"\n  1b. Fetching instrument info for Apple ({apple_isin}):")
    apple_info = await instrument_service.fetch_instrument(apple_isin)
    if apple_info:
        print(f"  - Name: {apple_info.get('shortName', 'N/A')}")
        print(f"  - Type: {apple_info.get('typeId', 'N/A')}")
        print(f"  - ISIN: {apple_info.get('isin', 'N/A')}")
        print(f"  - Company: {apple_info.get('company', {}).get('name', 'N/A')}")

    # 2. Fetch detailed instrument information
    print("\n" + "=" * 50)
    print("2. Fetching detailed instrument information...")
    print("-" * 50)

    print(f"\n  2a. Fetching detailed info for Bitcoin ({bitcoin_isin}):")
    bitcoin_details = await instrument_service.fetch_instrument_details(bitcoin_isin)
    if bitcoin_details:
        print(f"  - Keys available: {list(bitcoin_details.keys())}")
        print(f"  - Description available: {'description' in bitcoin_details}")
    else:
        print("  - No detailed information available")

    print(f"\n  2b. Fetching detailed info for Apple ({apple_isin}):")
    apple_details = await instrument_service.fetch_instrument_details(apple_isin)
    if apple_details:
        print(f"  - Keys available: {list(apple_details.keys())}")
        print(f"  - Description available: {'description' in apple_details}")
    else:
        print("  - No detailed information available")

    # 3. Fetch instrument suitability information
    print("\n" + "=" * 50)
    print("3. Fetching instrument suitability information...")
    print("-" * 50)

    print(f"\n  3a. Fetching suitability for Bitcoin ({bitcoin_isin}):")
    bitcoin_suitability = await instrument_service.fetch_instrument_suitability(bitcoin_isin)
    if bitcoin_suitability:
        print(f"  - Keys available: {list(bitcoin_suitability.keys())}")
        print("  - Suitability data retrieved successfully")
    else:
        print("  - No suitability information available")

    print(f"\n  3b. Fetching suitability for Apple ({apple_isin}):")
    apple_suitability = await instrument_service.fetch_instrument_suitability(apple_isin)
    if apple_suitability:
        print(f"  - Keys available: {list(apple_suitability.keys())}")
        print("  - Suitability data retrieved successfully")
    else:
        print("  - No suitability information available")

    # 4. Fetch stock-specific details
    print("\n" + "=" * 50)
    print("4. Fetching stock-specific details...")
    print("-" * 50)

    print(f"\n  Fetching stock details for Apple ({apple_isin}):")
    apple_stock_details = await instrument_service.fetch_stock_details(apple_isin)
    if apple_stock_details:
        print(f"  - Keys available: {list(apple_stock_details.keys())}")
        print("  - Stock-specific data retrieved successfully")
        # Display some common stock fields if available
        if "company" in apple_stock_details:
            company = apple_stock_details.get("company", {})
            print(f"  - Company name: {company.get('name', 'N/A')}")
            print(f"  - Country: {company.get('countryOfOrigin', 'N/A')}")
    else:
        print("  - No stock details available")

    print(f"\n  Note: Bitcoin ({bitcoin_isin}) is not a stock, stock_details may not be relevant")

    # 5. Fetch instruments by type
    print("\n" + "=" * 50)
    print("5. Fetching instruments by type...")
    print("-" * 50)

    instrument_types = ["crypto", "stock", "fund"]

    for instrument_type in instrument_types:
        print(
            f"\n  5.{instrument_types.index(instrument_type) + 1}. Fetching {instrument_type} instruments (first page):"
        )
        try:
            instruments_by_type = await instrument_service.fetch_instruments_by_type(instrument_type)
            print(f"  - Found {len(instruments_by_type)} result(s)")

            # Show first 3 instruments
            for i, instrument in enumerate(instruments_by_type[:3], 1):
                print(f"    {i}. {instrument.get('name', 'N/A')} ({instrument.get('isin', 'N/A')})")
        except Exception as e:
            print(f"  - Error: {e}")

    # 6. Fetch all instruments (WARNING: Very long operation)
    print("\n" + "=" * 50)
    print("6. Fetching all instruments (all types)...")
    print("-" * 50)
    print("WARNING: This operation can take a VERY long time!")
    print("It fetches ALL instruments of ALL types from Trade Republic.")
    # Uncomment to use (WARNING: Very long operation):
    # await instrument_service.fetch_instruments()
    # print("All instruments fetched successfully (check output folder)")

    # 7. Supported instrument types
    print("\n" + "=" * 50)
    print("7. Supported instrument types...")
    print("-" * 50)
    print("\nAvailable instrument types:")
    for inst_type in sorted(instrument_service.INSTRUMENT_TYPES):
        print(f"  - {inst_type}")

    print("\n" + "=" * 50)
    print("Instrument examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
