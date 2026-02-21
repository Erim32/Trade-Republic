import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    search_service = tr_client.search_service

    # 1. Basic search for instruments by query
    print("=" * 50)
    print("1. Basic search for instruments")
    print("-" * 50)

    print("\n  1a. Searching for 'Tesla' stocks:")
    results = await search_service.search_instruments(query="Tesla", asset_type="stock", page=1, page_size=10)
    print(f"  Found {len(results.get('results', []))} result(s)")
    for result in results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  1b. Searching for 'Bitcoin' crypto:")
    crypto_results = await search_service.search_instruments(query="Bitcoin", asset_type="crypto", page=1, page_size=10)
    print(f"  Found {len(crypto_results.get('results', []))} result(s)")
    for result in crypto_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  1c. Searching for 'Vanguard' funds:")
    fund_results = await search_service.search_instruments(query="Vanguard", asset_type="fund", page=1, page_size=10)
    print(f"  Found {len(fund_results.get('results', []))} result(s)")
    for result in fund_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    # 2. Advanced search with filters
    print("\n" + "=" * 50)
    print("2. Advanced search with filters")
    print("-" * 50)

    print("\n  2a. Search with country filter (Germany):")
    country_filter_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_country="DE"
    )
    print(f"  Found {len(country_filter_results.get('results', []))} result(s)")
    for result in country_filter_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  2b. Search with sector filter (Technology):")
    sector_filter_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_sector="Technology"
    )
    print(f"  Found {len(sector_filter_results.get('results', []))} result(s)")
    for result in sector_filter_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  2c. Search with multiple filters (US Tech stocks):")
    multi_filter_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_country="US", filter_sector="Technology"
    )
    print(f"  Found {len(multi_filter_results.get('results', []))} result(s)")
    for result in multi_filter_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  2d. Search with aggregate option:")
    aggregate_results = await search_service.search_instruments(
        query="Apple", asset_type="stock", page=1, page_size=10, aggregate=True
    )
    print(f"  Found {len(aggregate_results.get('results', []))} result(s)")

    print("\n  2e. Search only savable instruments:")
    savable_results = await search_service.search_instruments(
        query="Apple", asset_type="stock", page=1, page_size=10, only_savable=True
    )
    print(f"  Found {len(savable_results.get('results', []))} result(s)")

    print("\n  2f. Search with region filter:")
    region_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_region="Europe"
    )
    print(f"  Found {len(region_results.get('results', []))} result(s)")

    print("\n  2g. Search with jurisdiction filter:")
    jurisdiction_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_jurisdiction="EU"
    )
    print(f"  Found {len(jurisdiction_results.get('results', []))} result(s)")

    print("\n  2h. Search with index filter:")
    index_results = await search_service.search_instruments(
        query="", asset_type="stock", page=1, page_size=10, filter_index="DAX"
    )
    print(f"  Found {len(index_results.get('results', []))} result(s)")

    # 3. Search by country (convenience method)
    print("\n" + "=" * 50)
    print("3. Search by country (convenience method)")
    print("-" * 50)

    print("\n  3a. Stocks from Germany:")
    country_results = await search_service.search_by_country(country="DE", asset_type="stock", page=1, page_size=10)
    print(f"  Found {len(country_results.get('results', []))} result(s)")
    for result in country_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  3b. Stocks from United States:")
    us_results = await search_service.search_by_country(country="US", asset_type="stock", page=1, page_size=10)
    print(f"  Found {len(us_results.get('results', []))} result(s)")
    for result in us_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  3c. Stocks from France:")
    fr_results = await search_service.search_by_country(country="FR", asset_type="stock", page=1, page_size=10)
    print(f"  Found {len(fr_results.get('results', []))} result(s)")
    for result in fr_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    # 4. Search by sector (convenience method)
    print("\n" + "=" * 50)
    print("4. Search by sector (convenience method)")
    print("-" * 50)

    print("\n  4a. Technology sector:")
    tech_results = await search_service.search_by_sector(sector="Technology", asset_type="stock", page=1, page_size=10)
    print(f"  Found {len(tech_results.get('results', []))} result(s)")
    for result in tech_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  4b. Healthcare sector:")
    health_results = await search_service.search_by_sector(
        sector="Healthcare", asset_type="stock", page=1, page_size=10
    )
    print(f"  Found {len(health_results.get('results', []))} result(s)")
    for result in health_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    print("\n  4c. Financial sector:")
    finance_results = await search_service.search_by_sector(
        sector="Financials", asset_type="stock", page=1, page_size=10
    )
    print(f"  Found {len(finance_results.get('results', []))} result(s)")
    for result in finance_results.get("results", [])[:3]:
        print(f"    - {result.get('name')} ({result.get('isin')})")

    # 5. Get available search tags
    print("\n" + "=" * 50)
    print("5. Getting available search tags")
    print("-" * 50)
    tags = await search_service.get_search_tags()
    print(f"  Available tags: {list(tags.keys()) if tags else 'None'}")
    if tags:
        for key, value in list(tags.items())[:5]:  # Show first 5 tags
            print(f"    - {key}: {value if isinstance(value, (str, int)) else type(value).__name__}")

    # 6. Get suggested tags for queries
    print("\n" + "=" * 50)
    print("6. Getting suggested tags for queries")
    print("-" * 50)

    queries = ["tech", "energy", "bank", "pharma"]
    for query in queries:
        print(f"\n  Suggested tags for '{query}':")
        suggested = await search_service.get_suggested_tags(query)
        if suggested:
            suggestions = suggested.get("suggestions", [])
            print(f"    Found {len(suggestions)} suggestion(s)")
            for suggestion in suggestions[:5]:  # Show first 5
                print(f"      - {suggestion}")
        else:
            print("    No suggestions found")

    # 7. Pagination example
    print("\n" + "=" * 50)
    print("7. Pagination example")
    print("-" * 50)

    print("\n  Fetching multiple pages for 'ETF' search:")
    for page_num in range(1, 4):  # Pages 1, 2, 3
        page_results = await search_service.search_instruments(
            query="ETF", asset_type="fund", page=page_num, page_size=5
        )
        print(f"  Page {page_num}: {len(page_results.get('results', []))} result(s)")
        for result in page_results.get("results", []):
            print(f"    - {result.get('name')}")

    print("\n" + "=" * 50)
    print("Search examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
