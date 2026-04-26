import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.business.market_data_service import MarketDataService
from trade_republic.tr_client import TRClient  # noqa: E402
from trade_republic.utils.tr_utils import TRUtils  # noqa: E402


async def main():
    PROJECT_NAME = "04_extract_isins_with_last_prices"
    INPUT_FOLDER = os.path.join("output", "examples", "02_extract_isins")
    OUTPUT_FOLDER = os.path.join("output", "examples", PROJECT_NAME)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize the TRClient, Works only with only 1 concurrent connection to avoid hitting rate limits when fetching instruments
    tr_client = TRClient(phone="", pin="", output_folder=OUTPUT_FOLDER, max_concurrent_connections=1)
    market_data_service: MarketDataService = tr_client.market_data_service

    # Load instruments from file if already saved, otherwise fetch and save
    instruments = TRUtils.load_json_from_file("02_all_instruments_with_infos.json", output_folder=INPUT_FOLDER)

    def count_isins_by_exchanges(instruments: list[dict]) -> dict:
        exchanges_count = {}
        for instrument in instruments:
            instrument_info = instrument.get("instrument_info", {})
            exchanges = instrument_info.get("exchanges", [])
            for exchange in exchanges:
                exchange_slug = exchange.get("slug")
                if exchange_slug:
                    exchanges_count[exchange_slug] = exchanges_count.get(exchange_slug, 0) + 1
        return exchanges_count

    def display_exchanges_count(exchanges_count: dict):
        print("Exchanges count:")
        for exchange_slug, count in exchanges_count.items():
            print(f"   - {exchange_slug}: {count}")

    print("Counting ISINs by exchanges...")
    dict_exchanges_count = count_isins_by_exchanges(instruments)
    display_exchanges_count(dict_exchanges_count)

    # Enrich instruments with instrument_info
    enriched_instruments = []
    cpt_instruments = len(instruments)
    cpt = 0
    # instruments = []
    # instruments.append({"isin": "XF000XRP0018", "instrument_info": {"exchanges": [{"slug": "WMT", "active": True}]}})
    # skip 750 first instruments
    # {slug: count

    # cpt += 1
    # print(f"Fetching ticker details for ISIN: {isin} ({cpt}/{cpt_instruments})")
    # exchanges = instrument["instrument_info"].get("exchanges", [])
    # instrument["tickers"] = {}
    # for exchange in exchanges:
    #     exchange_slug = exchange.get("slug")
    #     is_active = exchange.get("active", False)
    #     instrument["tickers"][exchange_slug] = {}
    #     if is_active:
    #         INGORE_EXCHANGES = [
    #             "WMT",
    #             "FRA",
    #             "XFRA",
    #             "XSWX",
    #             "XHKG",
    #             "XCSE",
    #             "XNYS",
    #             "XASX",
    #             "TIB",
    #             "XSTO",
    #             "XHEL",
    #             "XPAR",
    #             "XLIS",
    #             "XNAS",
    #             "TDG",
    #         ]  # skip WMT exchange as it causes issues and is not relevant for price fetching
    #         isin_exchange = f"{isin}.{exchange_slug}"
    #         INGORE_ISIN_EXCHANGES = ["CH1351577726.LSX", "CA23343T2039.LSX"]
    #         if (
    #             not exchange_slug.upper().strip() in INGORE_EXCHANGES
    #             and not isin_exchange.upper().strip() in INGORE_ISIN_EXCHANGES
    #         ):
    #             print(f"Fetching market info for ISIN: {isin}.{exchange_slug}")
    #             instrument["tickers"][exchange_slug] = await market_data_service.fetch_ticker(
    #                 isin, exchange_slug
    #             )
    #         else:
    #             print(f"Skipping inactive exchange {isin_exchange}")
    # enriched_instruments.append(instrument)

    # TRUtils.save_json(
    #     enriched_instruments,
    #     "04_all_instruments_with_last_prices.json",
    #     output_folder=OUTPUT_FOLDER,
    # )


if __name__ == "__main__":
    asyncio.run(main())
