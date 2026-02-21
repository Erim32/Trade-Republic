import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402
from trade_republic.utils.tr_utils import TRUtils  # noqa: E402


async def main():
    PROJECT_NAME = "03_compare_prices_and_spread"
    OUTPUT_FOLDER = os.path.join("output", "examples", PROJECT_NAME)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    tr_client = TRClient(phone="", pin="", output_folder=OUTPUT_FOLDER)
    market_data_service = tr_client.market_data_service
    instrument_service = tr_client.instrument_service

    ISIN = "XF000BTC0017"  # Bitcoin ISIN

    instrument = await instrument_service.fetch_instrument(ISIN)
    exchanges = instrument.get("exchanges", [])
    exchanges = [exchange for exchange in exchanges if exchange.get("active", True)]
    prices: list = []
    for exchange in exchanges:
        exchange["price"] = await market_data_service.fetch_ticker(ISIN, exchange["slug"])
        ask = float(exchange["price"].get("ask", {}).get("price"))
        bid = float(exchange["price"].get("bid", {}).get("price"))
        last = float(exchange["price"].get("last", {}).get("price"))
        spread = ask - bid if ask is not None and bid is not None else None
        last_time = exchange["price"].get("last", {}).get("time")

        prices.append(
            {
                "slug": exchange["slug"],
                "symbolAtExchange": exchange.get("symbolAtExchange"),
                "ask": ask,
                "bid": bid,
                "last": last,
                "spread": spread,
                "spreadPercent": ((spread / ask) * 100 if spread is not None and ask is not None else None),
                "lastTime": last_time,
            }
        )

    # sort by price["lastTime"] desc
    prices.sort(key=lambda x: x["lastTime"], reverse=True)

    for price in prices:
        print(
            f"Exchange: {price['slug']},"
            f" Ask: {price['ask']},"
            f" Bid: {price['bid']},"
            f" Last: {price['last']},"
            f" Spread: {price['spread']},"
            f" Spread%: {price['spreadPercent']}%,"
            f" Last Time: {price['lastTime']}"
            f"{'=' * 50}"
        )

    TRUtils.save_json(prices, f"{ISIN}_prices.json", output_folder=OUTPUT_FOLDER)


if __name__ == "__main__":
    asyncio.run(main())
