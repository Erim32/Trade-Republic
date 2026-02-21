import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    market_data_service = tr_client.market_data_service

    # Example ISINs
    bitcoin_isin = "XF000BTC0017"  # Bitcoin
    apple_isin = "US0378331005"  # Apple Inc.

    # 1. Fetch ticker data for specific exchanges
    print("=" * 50)
    print("1. Fetching ticker data for specific exchanges...")
    print("-" * 50)

    print("\n  1a. Bitcoin ticker on BHS exchange:")
    ticker_bhs = await market_data_service.fetch_ticker(bitcoin_isin, "BHS")
    if ticker_bhs:
        print(f"  - Bid price: {ticker_bhs.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {ticker_bhs.get('ask', {}).get('price', 'N/A')} EUR")
        print(f"  - Bid time: {ticker_bhs.get('bid', {}).get('time', 'N/A')}")

    print("\n  1b. Bitcoin ticker on B2C exchange:")
    ticker_b2c = await market_data_service.fetch_ticker(bitcoin_isin, "B2C")
    if ticker_b2c:
        print(f"  - Bid price: {ticker_b2c.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {ticker_b2c.get('ask', {}).get('price', 'N/A')} EUR")
        print(f"  - Bid time: {ticker_b2c.get('bid', {}).get('time', 'N/A')}")

    print("\n  1c. Apple ticker on LSX exchange:")
    ticker_apple = await market_data_service.fetch_ticker(apple_isin, "LSX")
    if ticker_apple:
        print(f"  - Bid price: {ticker_apple.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {ticker_apple.get('ask', {}).get('price', 'N/A')} EUR")

    # 2. Resolve used exchange (auto-detection)
    print("\n" + "=" * 50)
    print("2. Resolving used exchange (auto-detection)...")
    print("-" * 50)

    print(f"\n  2a. Finding best exchange for Bitcoin ({bitcoin_isin}):")
    bitcoin_exchange = await market_data_service.resolve_used_exchange(bitcoin_isin)
    print(f"  - Recommended exchange: {bitcoin_exchange}")

    print(f"\n  2b. Finding best exchange for Apple ({apple_isin}):")
    apple_exchange = await market_data_service.resolve_used_exchange(apple_isin)
    print(f"  - Recommended exchange: {apple_exchange}")

    # 3. Fetch last price (with auto-resolution)
    print("\n" + "=" * 50)
    print("3. Fetching last price (with auto-resolution)...")
    print("-" * 50)

    print("\n  3a. Last price for Bitcoin (auto-resolved exchange):")
    price_bitcoin_auto = await market_data_service.fetch_last_price(bitcoin_isin)
    if price_bitcoin_auto:
        print(f"  - Bid price: {price_bitcoin_auto.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {price_bitcoin_auto.get('ask', {}).get('price', 'N/A')} EUR")

    print("\n  3b. Last price for Bitcoin on specific exchange (BHS):")
    price_bitcoin_bhs = await market_data_service.fetch_last_price(bitcoin_isin, "BHS")
    if price_bitcoin_bhs:
        print(f"  - Bid price: {price_bitcoin_bhs.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {price_bitcoin_bhs.get('ask', {}).get('price', 'N/A')} EUR")

    print("\n  3c. Last price for Apple (auto-resolved exchange):")
    price_apple = await market_data_service.fetch_last_price(apple_isin)
    if price_apple:
        print(f"  - Bid price: {price_apple.get('bid', {}).get('price', 'N/A')} EUR")
        print(f"  - Ask price: {price_apple.get('ask', {}).get('price', 'N/A')} EUR")

    # 4. Watchlist management
    print("\n" + "=" * 50)
    print("4. Watchlist management...")
    print("-" * 50)

    print("\n  4a. Fetching current watchlist:")
    watchlist = await market_data_service.fetch_watchlist()
    watchlist_items = watchlist.get("items", [])
    print(f"  - Total items in watchlist: {len(watchlist_items)}")

    if watchlist_items:
        print("\n  Current watchlist items (first 5):")
        for i, item in enumerate(watchlist_items[:5], 1):
            print(f"    {i}. ISIN: {item.get('isin', 'N/A')}")
            print(f"       Name: {item.get('name', 'N/A')}")
    else:
        print("  - Watchlist is empty")

    # 4b. Add to watchlist (COMMENTED - modifies user's watchlist)
    print("\n  4b. Adding instrument to watchlist...")
    test_isin = bitcoin_isin
    add_response = await market_data_service.add_to_watchlist(test_isin)
    print(f"Add to watchlist response: {add_response}")
    updated_watchlist = await market_data_service.fetch_watchlist()
    print(f"Updated watchlist count: {len(updated_watchlist.get('items', []))}")

    # 4c. Remove from watchlist (COMMENTED - modifies user's watchlist)
    print("\n  4c. Removing instrument from watchlist...")
    remove_response = await market_data_service.remove_from_watchlist(test_isin)
    print(f"Remove from watchlist response: {remove_response}")
    updated_watchlist = await market_data_service.fetch_watchlist()
    print(f"Updated watchlist count: {len(updated_watchlist.get('items', []))}")

    # 5. News management
    print("\n" + "=" * 50)
    print("5. News management...")
    print("-" * 50)

    print(f"\n  5a. Fetching news for Bitcoin ({bitcoin_isin}):")
    bitcoin_news = await market_data_service.fetch_news(bitcoin_isin)
    bitcoin_news_items = bitcoin_news.get("items", [])
    print(f"  - Total news items: {len(bitcoin_news_items)}")

    if bitcoin_news_items:
        print("\n  Latest news (first 3):")
        for i, news in enumerate(bitcoin_news_items[:3], 1):
            print(f"    {i}. {news.get('headline', 'N/A')}")
            print(f"       Date: {news.get('createdAt', 'N/A')}")
            print(f"       Source: {news.get('source', {}).get('name', 'N/A')}")

    print(f"\n  5b. Fetching news for Apple ({apple_isin}):")
    apple_news = await market_data_service.fetch_news(apple_isin)
    apple_news_items = apple_news.get("items", [])
    print(f"  - Total news items: {len(apple_news_items)}")

    if apple_news_items:
        print("\n  Latest news (first 3):")
        for i, news in enumerate(apple_news_items[:3], 1):
            print(f"    {i}. {news.get('headline', 'N/A')}")
            print(f"       Date: {news.get('createdAt', 'N/A')}")

    # 6. News subscriptions management
    print("\n" + "=" * 50)
    print("6. News subscriptions management...")
    print("-" * 50)

    print("\n  6a. Fetching current news subscriptions:")
    subscriptions = await market_data_service.fetch_news_subscriptions()
    subscription_items = subscriptions.get("subscriptions", [])
    print(f"  - Total subscriptions: {len(subscription_items)}")

    if subscription_items:
        print("\n  Current subscriptions (first 5):")
        for i, sub in enumerate(subscription_items[:5], 1):
            print(f"    {i}. ISIN: {sub.get('isin', 'N/A')}")
            print(f"       Name: {sub.get('name', 'N/A')}")
    else:
        print("  - No active news subscriptions")

    # 6b. Subscribe to news
    print("\n  6b. Subscribing to news...")
    subscribe_response = await market_data_service.subscribe_to_news(test_isin)
    print(f"Subscribe response: {subscribe_response}")
    updated_subs = await market_data_service.fetch_news_subscriptions()
    print(f"Updated subscriptions count: {len(updated_subs.get('subscriptions', []))}")

    # 6c. Unsubscribe from news
    print("\n  6c. Unsubscribing from news...")
    unsubscribe_response = await market_data_service.unsubscribe_from_news(test_isin)
    print(f"Unsubscribe response: {unsubscribe_response}")
    updated_subs = await market_data_service.fetch_news_subscriptions()
    print(f"Updated subscriptions count: {len(updated_subs.get('subscriptions', []))}")

    # 7. Price comparison across exchanges
    print("\n" + "=" * 50)
    print("7. Price comparison across exchanges...")
    print("-" * 50)

    print("\n  Comparing Bitcoin prices across exchanges:")
    exchanges_to_test = ["BHS", "B2C"]

    for exchange in exchanges_to_test:
        ticker = await market_data_service.fetch_ticker(bitcoin_isin, exchange)
        if ticker:
            bid = ticker.get("bid", {}).get("price", "N/A")
            ask = ticker.get("ask", {}).get("price", "N/A")
            print(f"  - {exchange}: Bid={bid}, Ask={ask}")

    print("\n" + "=" * 50)
    print("Market data examples completed!")
    print("\n⚠️  NOTE: Watchlist and news subscription modifications are COMMENTED")
    print("   to prevent accidental changes. Uncomment carefully before use.")


if __name__ == "__main__":
    asyncio.run(main())
